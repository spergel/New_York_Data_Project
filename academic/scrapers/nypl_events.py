import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import hashlib
from event_filter import filter_events, get_filter_stats
from category_utils import determine_categories

NY_TZ = ZoneInfo("America/New_York")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_nypl_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar', 'livestream']):
        return "loc_virtual"
    
    # Major NYPL branches
    if 'schomburg' in location_str:
        return "loc_nypl_schomburg"
    if 'stephen a. schwarzman' in location_str or 'schwarzman' in location_str:
        return "loc_nypl_schwarzman"
    if 'lincoln center' in location_str:
        return "loc_nypl_lincoln"
    if 'mid-manhattan' in location_str:
        return "loc_nypl_midmanhattan"
    
    # Try to extract branch name for location ID
    branch_match = re.search(r'([a-z]+(?:\s+[a-z]+)?)\s+library', location_str, re.IGNORECASE)
    if branch_match:
        branch_name = branch_match.group(1).lower().replace(' ', '_')
        return f"loc_nypl_{branch_name}"
    
    return "loc_nypl_main"  # Default

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "New York Public Library",
            "address": "476 5th Ave, New York, NY 10018",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar', 'livestream']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Major branches with known addresses
    location_lower = location_str.lower()
    if 'schomburg' in location_lower:
        return {
            "name": "Schomburg Center for Research in Black Culture",
            "address": "515 Malcolm X Blvd, New York, NY 10037",
            "type": "venue"
        }
    if 'stephen a. schwarzman' in location_lower or 'schwarzman' in location_lower:
        return {
            "name": "Stephen A. Schwarzman Building",
            "address": "476 5th Ave, New York, NY 10018",
            "type": "venue"
        }
    if 'lincoln center' in location_lower:
        return {
            "name": "New York Public Library for the Performing Arts",
            "address": "40 Lincoln Center Plaza, New York, NY 10023",
            "type": "venue"
        }
    
    # Generic branch
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title and description."""
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    
    if any(term in title + ' ' + description for term in ['lecture', 'talk', 'discussion', 'presentation']):
        return "Seminar"
    elif any(term in title + ' ' + description for term in ['workshop', 'class', 'training']):
        return "Workshop"
    elif any(term in title + ' ' + description for term in ['reading', 'book', 'author', 'poetry']):
        return "Reading"
    elif any(term in title + ' ' + description for term in ['exhibition', 'exhibit', 'art', 'gallery']):
        return "Exhibition"
    elif any(term in title + ' ' + description for term in ['performance', 'concert', 'music', 'theater']):
        return "Performance"
    elif any(term in title + ' ' + description for term in ['film', 'movie', 'screening']):
        return "Film"
    
    return "Seminar"  # Default type for library events

def parse_time_range(time_str):
    """Parse time range like '6:30 PM - 8:00 PM' or '2:00 PM'"""
    if not time_str:
        return None, None
    
    time_str = time_str.strip()
    
    # Try to find time range
    time_range_match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*[-–]\s*(\d{1,2}):(\d{2})\s*(AM|PM)', time_str, re.IGNORECASE)
    if time_range_match:
        start_hour = int(time_range_match.group(1))
        start_min = int(time_range_match.group(2))
        start_ampm = time_range_match.group(3).upper()
        end_hour = int(time_range_match.group(4))
        end_min = int(time_range_match.group(5))
        end_ampm = time_range_match.group(6).upper()
        
        # Convert to 24-hour
        if start_ampm == 'PM' and start_hour != 12:
            start_hour += 12
        elif start_ampm == 'AM' and start_hour == 12:
            start_hour = 0
        if end_ampm == 'PM' and end_hour != 12:
            end_hour += 12
        elif end_ampm == 'AM' and end_hour == 12:
            end_hour = 0
        
        return (start_hour, start_min), (end_hour, end_min)
    
    # Try single time
    single_time_match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str, re.IGNORECASE)
    if single_time_match:
        hour = int(single_time_match.group(1))
        minute = int(single_time_match.group(2))
        ampm = single_time_match.group(3).upper()
        
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        
        return (hour, minute), None
    
    return None, None

def fetch_nypl_events(num_pages=3):
    """Fetch events from NYPL calendar"""
    base_url = "https://www.nypl.org/events/calendar"
    all_events = []
    
    # Calculate date 2 weeks from now for filtering
    future_date = (datetime.now(NY_TZ) + timedelta(days=14)).strftime("%m/%d/%Y")
    
    for page in range(1, num_pages + 1):
        # Build URL with params - handle multiple city[] values by constructing URL manually
        # NYPL expects: city[]=bx&city[]=man
        url = f"{base_url}?keyword=&target%5B%5D=ad&city%5B%5D=bx&city%5B%5D=man&date_op=GREATER_EQUAL&date1={future_date.replace('/', '%2F')}&location=&type=4322&topic=&audience=4334&series="
        if page > 1:
            url += f"&page={page}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # NYPL uses table rows for events
            event_rows = soup.find_all('tr', class_='col-4')
            
            print(f"Page {page}: Found {len(event_rows)} event rows")
            
            for row in event_rows:
                event = {}
                
                # Extract date/time from first td with class 'event-time'
                time_cell = row.find('td', class_='views-field event-time')
                if time_cell:
                    time_text = time_cell.get_text(separator=' ', strip=True)
                    # Format is like "Mon, December 8 @ 6:30 PM" or "Tue, December 9 @ 4 PM"
                    event['date_time_text'] = time_text
                
                # Extract title and URL from event-name div
                title_cell = row.find('td', class_='views-field event-title')
                if not title_cell:
                    # Try alternative selector
                    title_cell = row.find('td', class_=lambda x: x and 'event-title' in x)
                
                if title_cell:
                    name_div = title_cell.find('div', class_='event-name')
                    if not name_div:
                        # Try finding link directly
                        link = title_cell.find('a')
                    else:
                        link = name_div.find('a')
                    
                    if link:
                        event['title'] = link.get_text(strip=True)
                        href = link.get('href', '')
                        if href:
                            if href.startswith('/'):
                                event['url'] = f"https://www.nypl.org{href}"
                            else:
                                event['url'] = href
                    
                    # Extract description
                    desc_div = title_cell.find('div', class_='description')
                    if desc_div:
                        event['description'] = desc_div.get_text(strip=True)
                
                # Extract location
                location_cell = row.find('td', class_='views-field event-location')
                if location_cell:
                    event['location'] = location_cell.get_text(strip=True)
                
                if event.get('title'):
                    all_events.append(event)
            
            # Check if there are more pages
            if not event_rows:
                break
                
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            continue
    
    return all_events

def parse_nypl_events(events):
    """Parse and standardize NYPL events"""
    standardized_events = []
    
    for event in events:
        try:
            title = event.get('title', '').strip()
            if not title:
                continue
            
            # Parse date and time from date_time_text
            # Format: "Mon, December 8 @ 6:30 PM" or "Tue, December 9 @ 4 PM"
            date_obj = None
            start_time = None
            end_time = None
            
            date_time_text = event.get('date_time_text', '')
            if date_time_text:
                # Pattern: "Mon, December 8 @ 6:30 PM" or "Tue, December 9 @ 4 PM"
                # Extract date part: "Mon, December 8" or "Tue, December 9"
                date_match = re.search(r'([A-Z][a-z]{2}),\s+([A-Z][a-z]+)\s+(\d{1,2})', date_time_text)
                if date_match:
                    month_name = date_match.group(2)
                    day = int(date_match.group(3))
                    # Get current year, but adjust if date is in past
                    current_year = datetime.now(NY_TZ).year
                    try:
                        month_num = datetime.strptime(month_name, "%B").month
                        date_obj = datetime(current_year, month_num, day, tzinfo=NY_TZ)
                        # If date is more than 6 months in the past, assume next year
                        if date_obj < datetime.now(NY_TZ) - timedelta(days=180):
                            date_obj = date_obj.replace(year=current_year + 1)
                    except:
                        pass
                
                # Extract time part: "@ 6:30 PM" or "@ 4 PM"
                time_match = re.search(r'@\s+(\d{1,2})(?::(\d{2}))?\s*(AM|PM)', date_time_text, re.IGNORECASE)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    ampm = time_match.group(3).upper()
                    
                    # Convert to 24-hour
                    if ampm == 'PM' and hour != 12:
                        hour += 12
                    elif ampm == 'AM' and hour == 12:
                        hour = 0
                    
                    start_time = (hour, minute)
            
            # Create datetime objects
            if date_obj:
                if start_time:
                    start_datetime = date_obj.replace(hour=start_time[0], minute=start_time[1])
                else:
                    # Default to 6 PM if no time specified
                    start_datetime = date_obj.replace(hour=18, minute=0)
                
                # Default to 2 hours duration (NYPL events are typically 1-2 hours)
                end_datetime = start_datetime + timedelta(hours=2)
            else:
                # Skip if we can't parse date
                continue
            
            # Get location details
            location_str = event.get('location', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)
            
            # Create event ID
            url = event.get('url', '')
            event_id = f"evt_nypl_{hashlib.md5((url + title).encode()).hexdigest()[:8]}"
            
            # Create event data for categorization
            event_data = {
                "title": title,
                "description": event.get('description', '')
            }
            
            # Create metadata
            metadata = {
                "source_url": url,
                "source_name": "NYPL Events Calendar",
                "venue": venue,
                "organizer": {
                    "name": "New York Public Library",
                    "type": "organizer"
                }
            }
            
            standardized_event = {
                "id": event_id,
                "name": title,
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_nypl",
                "description": event.get('description', ''),
                "start_date": start_datetime.isoformat(),
                "end_date": end_datetime.isoformat(),
                "category": determine_categories(event_data),
                "source": "nypl",
                "source_group": "nypl",
                "metadata": metadata
            }
            
            standardized_events.append(standardized_event)
            
        except Exception as e:
            print(f"Error processing event: {event.get('title', 'Unknown')}. Error: {str(e)}")
            continue
    
    # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")
    
    return {"events": filtered_events}

def scrape_nypl_events(num_pages=3):
    """Main scraping function"""
    raw_events = fetch_nypl_events(num_pages)
    return parse_nypl_events(raw_events)

def main():
    try:
        events = scrape_nypl_events()
        event_count = len(events.get('events', []))
        print(f"Successfully processed {event_count} NYPL events.")
        
        # Always save to file
        with open('nypl_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        
        if event_count > 0:
            print(f"Events saved to nypl_events_debug.json")
        else:
            print("WARNING: No events found. File saved with empty events array.")
            return 1
            
    except Exception as e:
        print(f"ERROR: NYPL scraper crashed: {e}")
        import traceback
        traceback.print_exc()
        # Save empty result
        with open('nypl_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump({"events": []}, f, indent=2, ensure_ascii=False)
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)

