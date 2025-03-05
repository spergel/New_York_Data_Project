import requests
import json
from datetime import datetime, timezone
import re
import hashlib

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

def determine_categories(event_data):
    """Map Columbia categories to standard EventCategory enum values."""
    categories = set()
    all_tags = event_data.get('categories', [])
    
    category_mapping = {
        'science': 'SCIENCE',
        'technology': 'TECH',
        'engineering': 'TECH',
        'business': 'BUSINESS',
        'art': 'ARTS',
        'arts': 'ARTS',
        'culture': 'CULTURE',
        'education': 'EDUCATION',
        'health': 'HEALTH',
        'exercise': 'EXERCISE',
        'social': 'SOCIAL',
        'networking': 'NETWORKING'
    }
    
    # Add mapped categories
    for tag in all_tags:
        tag_lower = tag.lower()
        for key, value in category_mapping.items():
            if key in tag_lower:
                categories.add(value)
    
    # Ensure at least one category
    if not categories:
        categories.add('EDUCATION')
    
    return list(categories)

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
            start_date = datetime.strptime(event['start']['utcdate'], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(event['end']['utcdate'], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)

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
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "category": determine_categories(event),
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('summary', 'Unknown event')}. Error: {str(e)}")
            continue

    return standardized_events

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