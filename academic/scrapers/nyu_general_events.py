import requests
import json
from datetime import datetime, timedelta
import hashlib
import re

url = "https://as.nyu.edu/events/events-calendar/_jcr_content.search.json"

querystring = {"page":"0","span":"all","limit":"0"}

payload = ""
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://as.nyu.edu/events/events-calendar.html",
    "sec-ch-ua": '"Microsoft Edge";v="129", "Chromium";v="129", "Not?A_Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "x-requested-with": "XMLHttpRequest"
}

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_nyu_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific NYU buildings
    if any(term in location_str for term in ['warren weaver', 'wwh']):
        return "loc_nyu_wwh"
    if '60 fifth' in location_str:
        return "loc_nyu_60fifth"
    if 'bobst' in location_str:
        return "loc_nyu_bobst"
    if 'kimmel' in location_str:
        return "loc_nyu_kimmel"
    
    return "loc_nyu_main"  # Default to main campus

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "NYU Washington Square",
            "address": "New York, NY 10012",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Extract room number if present
    room_match = re.search(r'(?:room|rm\.?)\s*(\w+[-\d]+)', location_str, re.IGNORECASE)
    room_number = room_match.group(1) if room_match else None
    
    # Handle specific NYU buildings
    if any(term in location_str.lower() for term in ['warren weaver', 'wwh']):
        name = f"Warren Weaver Hall{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "251 Mercer St, New York, NY 10012",
            "type": "venue"
        }
    
    if '60 fifth' in location_str.lower():
        name = f"60 Fifth Avenue{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "60 Fifth Avenue, New York, NY 10011",
            "type": "venue"
        }
    
    if 'bobst' in location_str.lower():
        name = f"Bobst Library{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "70 Washington Square S, New York, NY 10012",
            "type": "venue"
        }
    
    if 'kimmel' in location_str.lower():
        name = f"Kimmel Center{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "60 Washington Square S, New York, NY 10012",
            "type": "venue"
        }
    
    # Default case - just clean up the location string
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title and description."""
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    department = event_data.get('department', '').lower()
    
    if any(term in title + description for term in ['seminar', 'colloquium', 'lecture']):
        return "Seminar"
    elif any(term in title + description for term in ['workshop', 'training']):
        return "Workshop"
    elif any(term in title + description for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + description for term in ['performance', 'concert', 'show']):
        return "Performance"
    elif any(term in description for term in ['thesis', 'dissertation', 'defense']):
        return "Defense"
    
    return "Academic"

def determine_categories(event_data):
    """Map NYU categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    department = event_data.get('department', '').lower()
    
    # Add categories based on content
    if any(term in title + description + department for term in ['math', 'mathematics', 'theorem']):
        categories.add('MATH')
    if any(term in title + description + department for term in ['computer', 'programming', 'software']):
        categories.add('TECH')
    if any(term in title + description + department for term in ['physics', 'chemistry', 'biology']):
        categories.add('SCIENCE')
    if any(term in title + description + department for term in ['art', 'music', 'performance']):
        categories.add('ARTS')
    if any(term in title + description + department for term in ['history', 'historical']):
        categories.add('HISTORY')
    if any(term in title + description + department for term in ['literature', 'writing', 'poetry']):
        categories.add('LITERATURE')
    if any(term in title + description + department for term in ['social', 'society', 'community']):
        categories.add('SOCIAL')
    
    # If no specific category found, use EDUCATION as default
    if not categories:
        categories.add('EDUCATION')
    
    return list(categories)

def scrape_nyu_events():
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Received status code {response.status_code}")
        return None

def parse_nyu_general_events(input_data):
    standardized_events = []

    for event in input_data['events']:
        try:
            start_date = datetime.fromisoformat(event['start-date'])
            end_date = datetime.fromisoformat(event['end-date'])

            # If end date is before start date, assume it's the next day
            if end_date < start_date:
                end_date += timedelta(days=1)

            # Get location details
            venue = event.get('venue', '')
            address = event.get('address', '')
            location = venue + (f", {address}" if address else '') if venue else address
            location_id = get_location_id(location)
            venue_obj = standardize_venue(location)

            # Create event ID using hash of URL and title
            event_id = f"evt_nyu_{hashlib.md5((event.get('url', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Create metadata
            metadata = {
                "source_url": f"https://as.nyu.edu{event['url']}",
                "source_name": "NYU Events Calendar",
                "venue": venue_obj,
                "organizer": {
                    "name": event.get('department-program', 'New York University'),
                    "type": "organizer"
                },
                "additional_info": {
                    "department": event.get('department-program', ''),
                    "image_url": f"https://as.nyu.edu{event['image-url']}" if event.get('image-url') else '',
                    "is_online": event.get('is-online', False),
                    "is_inperson": event.get('is-inperson', False)
                }
            }

            event_data = {
                "title": event['title'],
                "description": event.get('summary', ''),
                "department": event.get('department-program', '')
            }

            standardized_event = {
                "id": event_id,
                "name": event['title'],
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_nyu",
                "description": event.get('summary', ''),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "category": determine_categories(event_data),
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('title', 'Unknown')}. Error: {str(e)}")
            continue

    return {"events": standardized_events}

def scrape_nyu_general_events():
    input_data = scrape_nyu_events()
    if not input_data:
        print("No events were found. The website structure might have changed.")
        return {"events": []}
    
    return parse_nyu_general_events(input_data)

def main():
    events = scrape_nyu_general_events()
    print(f"Successfully processed {len(events['events'])} NYU General events.")
    
    # Save to file for debugging
    if events['events']:
        with open('nyu_general_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to nyu_general_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()