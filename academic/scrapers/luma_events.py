import requests
import json
from datetime import datetime, timezone
import re
import hashlib
from event_filter import filter_events, get_filter_stats

def parse_ical_date(date_str):
    """Parse iCal date format (YYYYMMDDTHHMMSSZ) to datetime object."""
    if not date_str:
        return None
    
    try:
        # Handle iCal date format: YYYYMMDDTHHMMSSZ
        year = int(date_str[:4])
        month = int(date_str[4:6]) - 1  # Month is 0-indexed
        day = int(date_str[6:8])
        hour = int(date_str[9:11])
        minute = int(date_str[11:13])
        second = int(date_str[13:15])
        
        return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    except (ValueError, IndexError):
        return None

def format_date_for_display(date_obj):
    """Format datetime object to readable string."""
    if not date_obj:
        return "Date TBD"
    
    return date_obj.strftime("%B %d, %Y at %I:%M %p")

def clean_description(description):
    """Clean up iCal description text."""
    if not description:
        return ""
    
    # Remove common iCal artifacts
    cleaned = description.replace('\\n', '\n').replace('\\t', '\t').replace('\\,', ',').replace('\\;', ';').replace('\\:', ':')
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def extract_institution(organizer):
    """Extract institution from organizer field."""
    if not organizer:
        return "DeSciNYC"
    
    # Look for common patterns
    if 'DeSciNYC' in organizer:
        return "DeSciNYC"
    if 'Columbia' in organizer:
        return "Columbia University"
    if 'NYU' in organizer:
        return "New York University"
    if 'CUNY' in organizer:
        return "CUNY"
    
    return "DeSciNYC"

def parse_ical_content(ical_content):
    """Parse iCal content and extract events."""
    events = []
    lines = ical_content.split('\n')
    
    current_event = {}
    in_event = False
    
    for line in lines:
        line = line.strip()
        
        if line == 'BEGIN:VEVENT':
            in_event = True
            current_event = {}
        elif line == 'END:VEVENT':
            if in_event and current_event.get('summary'):
                event = create_event_from_ical(current_event)
                if event:
                    events.append(event)
            in_event = False
            current_event = {}
        elif in_event and ':' in line:
            key, value = line.split(':', 1)
            
            if key == 'SUMMARY':
                current_event['summary'] = value
            elif key == 'DESCRIPTION':
                current_event['description'] = value
            elif key == 'DTSTART':
                current_event['start_date'] = value
            elif key == 'DTEND':
                current_event['end_date'] = value
            elif key == 'LOCATION':
                current_event['location'] = value
            elif key == 'ORGANIZER':
                current_event['organizer'] = value
            elif key == 'URL':
                current_event['url'] = value
    
    return events

def create_event_from_ical(ical_event):
    """Convert iCal event to our standard format."""
    if not ical_event.get('summary'):
        return None
    
    # Parse dates
    start_date = parse_ical_date(ical_event.get('start_date'))
    end_date = parse_ical_date(ical_event.get('end_date'))
    
    # Format date for display
    date_str = format_date_for_display(start_date)
    
    # Extract institution
    institution = extract_institution(ical_event.get('organizer'))
    
    # Clean description
    description = clean_description(ical_event.get('description', ''))
    
    # Create event ID
    event_id = hashlib.md5(f"{ical_event['summary']}{ical_event.get('start_date', '')}".encode()).hexdigest()
    
    return {
        "id": event_id,
        "name": ical_event['summary'],  # Use 'name' for compatibility with filter
        "title": ical_event['summary'],  # Keep 'title' for display
        "institution": institution,
        "date": date_str,
        "description": description,
        "location": ical_event.get('location', 'Location TBD'),
        "category": "Science",
        "source_url": ical_event.get('url'),
        "source": "luma"
    }

def scrape_luma_events():
    """Scrape events from Luma calendar."""
    print("Scraping Luma events...")
    
    try:
        # Fetch iCal data
        url = "https://api2.luma.com/ics/get?entity=calendar&id=cal-wZRB9D5dtAO9FXa"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse iCal content
        events = parse_ical_content(response.text)
        
        print(f"Found {len(events)} Luma events")
        
        # Filter events
        filtered_events = filter_events(events)
        print(f"After filtering: {len(filtered_events)} events")
        
        return filtered_events
        
    except Exception as e:
        print(f"Error scraping Luma events: {e}")
        return []

if __name__ == "__main__":
    events = scrape_luma_events()
    
    # Save to debug file
    with open('luma_events_debug.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(events)} events to luma_events_debug.json")
