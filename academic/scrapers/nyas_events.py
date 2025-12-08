import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
import hashlib
import re
from event_filter import filter_events, get_filter_stats
from category_utils import determine_categories

def get_location_id(location_str, event_type):
    """Map location string to standard location ID."""
    if not location_str:
        # Check event type for virtual events
        if event_type and 'virtual' in event_type.lower():
            return "loc_virtual"
        return "loc_nyas_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    return "loc_nyas_main"  # Default to main location

def standardize_venue(location_str, event_type):
    """Create a standardized Venue object from location string."""
    # Check if it's a virtual event
    if event_type and 'virtual' in event_type.lower():
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    if not location_str:
        return {
            "name": "The New York Academy of Sciences",
            "address": "250 Greenwich St, New York, NY 10007",
            "type": "venue"
        }
    
    location_str_lower = location_str.lower()
    
    # Check for online venues
    if any(term in location_str_lower for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    return {
        "name": location_str or "The New York Academy of Sciences",
        "address": "250 Greenwich St, New York, NY 10007",
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title and description."""
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    text = f"{title} {description}"
    
    if any(term in text for term in ['symposium', 'conference', 'summit']):
        return "Conference"
    elif any(term in text for term in ['workshop', 'training', 'masterclass']):
        return "Workshop"
    elif any(term in text for term in ['lecture', 'talk', 'presentation']):
        return "Seminar"
    elif any(term in text for term in ['networking', 'speed networking']):
        return "Networking"
    elif any(term in text for term in ['movie', 'film', 'screening']):
        return "Screening"
    
    return "Seminar"  # Default for NYAS events

def determine_categories_nyas(event_data):
    """Determine categories for NYAS events."""
    categories = determine_categories(event_data, method='auto')
    
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    text_content = f"{title} {description}"
    
    # Science categories
    if any(term in text_content for term in ['genetics', 'dna', 'genome', 'molecular']):
        if 'BIOLOGY' not in categories:
            categories.append('BIOLOGY')
    
    if any(term in text_content for term in ['chemistry', 'chemical', 'biochemistry']):
        if 'CHEMISTRY' not in categories:
            categories.append('CHEMISTRY')
    
    if any(term in text_content for term in ['neuroscience', 'brain', 'cognitive', 'neural']):
        if 'NEUROSCIENCE' not in categories:
            categories.append('NEUROSCIENCE')
    
    if any(term in text_content for term in ['cancer', 'oncology', 'tumor', 'immunotherapy']):
        if 'MEDICINE' not in categories:
            categories.append('MEDICINE')
    
    if any(term in text_content for term in ['climate', 'environment', 'sustainability', 'planet']):
        if 'ENVIRONMENTAL' not in categories:
            categories.append('ENVIRONMENTAL')
    
    if any(term in text_content for term in ['ai', 'artificial intelligence', 'technology', 'tech', 'innovation']):
        if 'TECHNOLOGY' not in categories:
            categories.append('TECHNOLOGY')
    
    if any(term in text_content for term in ['anthropology', 'society', 'social']):
        if 'SOCIAL' not in categories:
            categories.append('SOCIAL')
    
    if any(term in text_content for term in ['investing', 'finance', 'business']):
        if 'BUSINESS' not in categories:
            categories.append('BUSINESS')
    
    # Ensure NYAS events get SCIENCE category
    if 'SCIENCE' not in categories:
        categories.append('SCIENCE')
    
    return categories

def parse_date(date_str):
    """Parse date string like 'Dec 01, 2025' or 'Feb 02 - 03, 2026'."""
    try:
        # Clean up the date string - remove extra spaces
        date_str = re.sub(r'\s+', ' ', date_str.strip())
        
        # Handle date ranges like "Feb 02 - 03, 2026"
        if ' - ' in date_str:
            # Take the start date
            parts = date_str.split(' - ')
            if len(parts) == 2:
                start_part = parts[0].strip()
                # Get the year from the second part
                year_match = re.search(r'(\d{4})', parts[1])
                if year_match:
                    year = year_match.group(1)
                    # Reconstruct start date with year
                    date_str = f"{start_part}, {year}"
        
        # Try different date formats
        formats = [
            "%b %d, %Y",  # Dec 01, 2025
            "%B %d, %Y",   # December 01, 2025
            "%b %d %Y",    # Dec 01 2025
            "%B %d %Y",   # December 01 2025
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date: {date_str}")
        return None
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

def fetch_nyas_events():
    """Fetch events from NYAS events calendar."""
    url = "https://www.nyas.org/shaping-science/events-calendar/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching NYAS events: {e}")
        return None

def parse_nyas_events(html_content):
    """Parse events from NYAS HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    events = []
    
    # Find all divs that contain event information
    # Events have a pattern: "Free for Members" (optional) + Event Type + Title + Date
    all_divs = soup.find_all('div')
    
    # Look for divs that contain both a date pattern and event type
    for div in all_divs:
        text = div.get_text()
        
        # Look for date pattern (with possible extra spaces)
        date_match = re.search(r'([A-Z][a-z]{2,3})\s+(\d{1,2})(?:\s*-\s*(\d{1,2}))?,\s+(\d{4})', text)
        if not date_match:
            continue
        
        # Check if this div has event-like content (title, event type)
        if not any(term in text.lower() for term in ['virtual event', 'hybrid event', 'in-person event', 'free for members']):
            continue
        
        # Extract event type
        event_type = 'In-person'
        if 'virtual event' in text.lower():
            event_type = 'Virtual'
        elif 'hybrid event' in text.lower():
            event_type = 'Hybrid'
        
        # Extract title - it's usually after "Free for Members" and event type, before the date
        # Title is typically on its own line
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        title = ''
        
        # Look for the title line (usually between event type and date)
        found_event_type = False
        for line in lines:
            if 'virtual event' in line.lower() or 'hybrid event' in line.lower() or 'in-person event' in line.lower():
                found_event_type = True
                continue
            if found_event_type and line and len(line) > 10:
                # Skip common non-title lines
                if line.lower() not in ['free for members', 'virtual event', 'hybrid event', 'in-person event']:
                    title = line
                    break
        
        # If no title found, try extracting from the div structure
        if not title or len(title) < 5:
            # Look for links or headings in the div
            link = div.find('a')
            if link:
                title = link.get_text(strip=True)
            else:
                heading = div.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if heading:
                    title = heading.get_text(strip=True)
        
        if not title or len(title) < 5:
            continue
        
        # Build date string
        month = date_match.group(1)
        day1 = date_match.group(2)
        day2 = date_match.group(3)
        year = date_match.group(4)
        
        if day2:
            date_str = f"{month} {day1} - {day2}, {year}"
        else:
            date_str = f"{month} {day1}, {year}"
        
        events.append({
            'date_str': date_str,
            'title': title,
            'event_type': event_type,
            'raw_text': text
        })
    
    print(f"Found {len(events)} events")
    
    # Remove duplicates based on title and date
    seen = set()
    unique_events = []
    for event in events:
        key = (event['title'], event['date_str'])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    print(f"After deduplication: {len(unique_events)} events")
    
    # Parse the found events
    standardized_events = []
    for event_data in unique_events:
        try:
            date_str = event_data.get('date_str', '')
            title = event_data.get('title', '')
            event_type = event_data.get('event_type', 'In-person')
            raw_text = event_data.get('raw_text', '')
            
            if not title or len(title) < 5:
                continue
            
            # Parse date - handle date ranges
            if ' - ' in date_str:
                # For date ranges, use the start date
                date_parts = date_str.split(' - ')
                start_date_str = date_parts[0] + date_str.split(', ')[-1] if ', ' in date_str else date_parts[0]
                start_date = parse_date(start_date_str)
            else:
                start_date = parse_date(date_str)
            
            if not start_date:
                continue
            
            # Default to 2-hour duration, set time to 6 PM if not specified
            if start_date.hour == 0 and start_date.minute == 0:
                start_date = start_date.replace(hour=18, minute=0)  # 6 PM default
            
            end_date = start_date.replace(hour=start_date.hour + 2)
            
            # Convert to NYC timezone
            from date_utils import standardize_datetime, NY_TZ
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=NY_TZ)
            else:
                start_date = start_date.astimezone(NY_TZ)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=NY_TZ)
            else:
                end_date = end_date.astimezone(NY_TZ)
            
            # Extract location if mentioned
            location = ''
            if event_type.lower() in ['in-person', 'hybrid']:
                location = 'The New York Academy of Sciences'
            
            # Create event data for categorization
            event_info = {
                "title": title,
                "description": raw_text[:500] if raw_text else ""
            }
            
            # Get location details
            location_id = get_location_id(location, event_type)
            venue = standardize_venue(location, event_type)
            
            # Create event ID
            event_id = f"evt_nyas_{hashlib.md5((title + date_str).encode()).hexdigest()[:8]}"
            
            # Create metadata
            metadata = {
                "source_url": f"https://www.nyas.org/shaping-science/events-calendar/",
                "source_name": "New York Academy of Sciences Events Calendar",
                "venue": venue,
                "organizer": {
                    "name": "The New York Academy of Sciences",
                    "type": "organizer"
                },
                "additional_info": {
                    "event_type": event_type,
                    "is_member_free": "Free for Members" in raw_text
                }
            }
            
            standardized_event = {
                "id": event_id,
                "name": title,
                "type": determine_event_type(event_info),
                "location_id": location_id,
                "community_id": "com_nyas",
                "description": raw_text[:500] if raw_text else title,
                "start_date": standardize_datetime(start_date),
                "end_date": standardize_datetime(end_date),
                "category": determine_categories_nyas(event_info),
                "source": "nyas",
                "source_group": "Independent",
                "metadata": metadata
            }
            
            standardized_events.append(standardized_event)
            
        except Exception as e:
            print(f"Error processing event: {e}")
            continue
    
    return standardized_events

def scrape_nyas_events():
    """Main scraping function."""
    html_content = fetch_nyas_events()
    if not html_content:
        return {"events": []}
    
    events = parse_nyas_events(html_content)
    
    # Apply event filtering
    print(f"Before filtering: {len(events)} events")
    filtered_events = filter_events(events)
    stats = get_filter_stats(events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")
    
    return {"events": filtered_events}

def main():
    events = scrape_nyas_events()
    print(f"Successfully processed {len(events['events'])} NYAS events.")
    
    # Save to file for debugging
    if events['events']:
        with open('nyas_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to nyas_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()

