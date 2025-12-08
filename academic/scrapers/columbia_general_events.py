import requests
import json
from datetime import datetime, timedelta
import re
import hashlib
from event_filter import filter_events, get_filter_stats
from category_utils import determine_categories
from date_utils import standardize_datetime, to_nyc_datetime, NY_TZ

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return None
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific Columbia buildings
    if 'pupin' in location_str:
        return "loc_columbia_pupin"
    if 'mudd' in location_str:
        return "loc_columbia_mudd"
    if 'butler' in location_str:
        return "loc_columbia_butler"
    if 'law' in location_str:
        return "loc_columbia_law"
    if 'sipa' in location_str or 'international affairs' in location_str:
        return "loc_columbia_sipa"
    
    # Default to main campus
    return "loc_columbia_main"

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return None
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Extract room number if present
    room_match = re.search(r'(?:room|rm\.?)\s*(\w+[-\d]+)', location_str, re.IGNORECASE)
    room_number = room_match.group(1) if room_match else None
    
    # Map to known buildings
    location_lower = location_str.lower()
    if 'pupin' in location_lower:
        name = f"Pupin Hall{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "538 W 120th St, New York, NY 10027",
            "type": "venue"
        }
    elif 'mudd' in location_lower:
        name = f"Mudd Building{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "500 W 120th St, New York, NY 10027",
            "type": "venue"
        }
    elif 'butler' in location_lower:
        name = f"Butler Library{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "535 W 114th St, New York, NY 10027",
            "type": "venue"
        }
    
    # Default case - just clean up the location string
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on categories and title."""
    title = event_data.get('summary', '').lower()
    categories = [cat.lower() for cat in event_data.get('categories', [])]
    
    if any(term in title for term in ['seminar', 'colloquium', 'lecture']):
        return "Seminar"
    elif any(term in title for term in ['workshop', 'training']):
        return "Workshop"
    elif any(term in title for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in categories + [title] for term in ['performance', 'concert', 'theater', 'theatre', 'dance']):
        return "Performance"
    elif any(term in categories + [title] for term in ['exhibition', 'gallery', 'museum']):
        return "Exhibition"
    
    return "Academic"

def determine_categories_columbia(event_data):
    """Determine categories for Columbia events using centralized logic."""
    # Use hybrid approach: tag mapping + keyword analysis
    categories = determine_categories(event_data, method='hybrid')
    
    # Columbia is strong in humanities, so prioritize humanities categories
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    text_content = f"{title} {description}"
    
    # Check for humanities-specific content
    humanities_keywords = [
        'history', 'literature', 'philosophy', 'classics', 'language', 'linguistics',
        'anthropology', 'archaeology', 'cultural studies', 'humanities', 'classical',
        'ancient', 'medieval', 'renaissance', 'modern', 'contemporary', 'criticism',
        'theory', 'text', 'manuscript', 'document', 'archive', 'heritage'
    ]
    
    if any(keyword in text_content for keyword in humanities_keywords):
        if 'HUMANITIES' not in categories:
            categories.append('HUMANITIES')
    
    # Ensure Columbia events get EDUCATION category
    if 'EDUCATION' not in categories:
        categories.append('EDUCATION')
    
    return categories

def fetch_columbia_events():
    url = "https://events.columbia.edu/feeder/main/eventsFeed.do?f=y&sort=dtstart.utc:asc&fexpr=(categories.href!=%22/public/.bedework/categories/sys/Ongoing%22)%20and%20(categories.href=%22/public/.bedework/categories/org/UniversityEvents%22)%20and%20(entity_type=%22event%22%7Centity_type=%22todo%22)&skinName=list-json&count=200"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # Attempt to clean the JSON string
            cleaned_json = re.sub(r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', response.text)
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                print("Failed to parse JSON even after cleaning.")
                return None
    else:
        print(f"Failed to fetch events. Status code: {response.status_code}")
        return None

def parse_columbia_events(input_data):
    standardized_events = []

    for event in input_data['bwEventList']['events']:
        try:
            # Get location details
            location_str = event.get('location', {}).get('address', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Process start and end dates
            # Columbia API returns times in UTC format (ending with Z)
            # However, these times appear to be in Eastern Time incorrectly labeled as UTC
            # We treat them as NYC time (America/New_York) and store in NYC timezone
            # Parse the date string (it's labeled UTC but is actually Eastern Time)
            naive_datetime = datetime.strptime(event['start']['utcdate'], "%Y%m%dT%H%M%SZ")
            # Treat as NYC time (America/New_York)
            start_date_dt = naive_datetime.replace(tzinfo=NY_TZ)
            
            naive_datetime_end = datetime.strptime(event['end']['utcdate'], "%Y%m%dT%H%M%SZ")
            end_date_dt = naive_datetime_end.replace(tzinfo=NY_TZ)
            
            # Standardize to ISO format (in NYC timezone)
            start_date = standardize_datetime(start_date_dt)
            end_date = standardize_datetime(end_date_dt)

            # Extract department/organizer
            department = None
            for xproperty in event.get('xproperties', []):
                if 'X-BEDEWORK-CALSUITE' in xproperty:
                    department = xproperty['X-BEDEWORK-CALSUITE']['values']['text']
                    break

            # Create event ID
            event_id = f"evt_columbia_{hashlib.md5((event['eventlink'] + event['summary']).encode()).hexdigest()[:8]}"

            # Create metadata
            metadata = {
                "source_url": event['eventlink'],
                "source_name": "Columbia University",
                "venue": venue,
                "organizer": {
                    "name": department or "Columbia University",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": department,
                    "tags": event.get('categories', []),
                    "audience": [tag for tag in event.get('categories', []) if any(prev_tag.lower() == 'audience' for prev_tag in event.get('categories', [])[:event.get('categories', []).index(tag)])]
                }
            }

            standardized_event = {
                "id": event_id,
                "name": event['summary'],
                "type": determine_event_type(event),
                "location_id": location_id,
                "community_id": "com_columbia_general",
                "description": event.get('description', ''),
                "start_date": start_date,
                "end_date": end_date,
                "category": determine_categories_columbia(event),
                "source": "columbia",
                "source_group": "Columbia",
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('summary', 'Unknown event')}. Error: {str(e)}")
            continue

    # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")

    return filtered_events

def scrape_columbia_events():
    data = fetch_columbia_events()
    if data is None:
        return None

    standardized_events = parse_columbia_events(data)
    return {"events": standardized_events}

def main():
    events = scrape_columbia_events()
    if events:
        print(f"Successfully processed {len(events['events'])} Columbia events.")
        # Save to file for debugging
        with open('columbia_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to columbia_events_debug.json")
    else:
        print("Failed to process Columbia events.")

if __name__ == "__main__":
    main()