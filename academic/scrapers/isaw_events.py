import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import hashlib

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_isaw_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific ISAW venues
    if 'lecture hall' in location_str:
        return "loc_isaw_lecture"
    if 'exhibition' in location_str:
        return "loc_isaw_gallery"
    if 'seminar room' in location_str:
        return "loc_isaw_seminar"
    if 'library' in location_str:
        return "loc_isaw_library"
    
    return "loc_isaw_main"  # Default to main building

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "Institute for the Study of the Ancient World",
            "address": "15 East 84th Street, New York, NY 10028",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle specific ISAW venues
    if 'lecture hall' in location_str.lower():
        return {
            "name": "ISAW Lecture Hall",
            "address": "15 East 84th Street, New York, NY 10028",
            "type": "venue"
        }
    
    if 'exhibition' in location_str.lower():
        return {
            "name": "ISAW Exhibition Gallery",
            "address": "15 East 84th Street, New York, NY 10028",
            "type": "venue"
        }
    
    if 'seminar room' in location_str.lower():
        return {
            "name": "ISAW Seminar Room",
            "address": "15 East 84th Street, New York, NY 10028",
            "type": "venue"
        }
    
    if 'library' in location_str.lower():
        return {
            "name": "ISAW Library",
            "address": "15 East 84th Street, New York, NY 10028",
            "type": "venue"
        }
    
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title and description."""
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    subtitle = event_data.get('subtitle', '').lower()
    
    if any(term in title + ' ' + description + ' ' + subtitle for term in ['lecture', 'talk']):
        return "Seminar"
    elif any(term in title + ' ' + description + ' ' + subtitle for term in ['workshop', 'class']):
        return "Workshop"
    elif any(term in title + ' ' + description + ' ' + subtitle for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + ' ' + description + ' ' + subtitle for term in ['exhibition', 'gallery']):
        return "Exhibition"
    elif any(term in title + ' ' + description + ' ' + subtitle for term in ['performance', 'concert']):
        return "Performance"
    
    return "Academic"  # Default type

def determine_categories(event_data):
    """Map ISAW categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    subtitle = event_data.get('subtitle', '').lower()
    
    # Add categories based on content
    if any(term in title + ' ' + description + ' ' + subtitle for term in ['archaeology', 'excavation', 'artifact']):
        categories.add('ARCHAEOLOGY')
    if any(term in title + ' ' + description + ' ' + subtitle for term in ['history', 'ancient', 'classical']):
        categories.add('HISTORY')
    if any(term in title + ' ' + description + ' ' + subtitle for term in ['art', 'sculpture', 'painting']):
        categories.add('ARTS')
    if any(term in title + ' ' + description + ' ' + subtitle for term in ['religion', 'ritual', 'mythology']):
        categories.add('RELIGION')
    if any(term in title + ' ' + description + ' ' + subtitle for term in ['science', 'technology', 'research']):
        categories.add('SCIENCE')
    
    # If no specific category found, use HISTORY as default for ISAW
    if not categories:
        categories.add('HISTORY')
    
    return list(categories)

def fetch_isaw_events():
    url = "https://isaw.nyu.edu/events"
    headers = {
        'User-Agent': 'ISAWEventScraper/1.0 (https://github.com/yourusername/your-repo; youremail@example.com)'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    events = []
    
    for event_div in soup.find_all('div', class_='event-result'):
        event = {}
        
        # Extract date and location
        header = event_div.find('div', class_='event-result-header')
        if header:
            spans = header.find_all('span')
            if len(spans) >= 2:
                event['datetime'] = spans[0].text.strip()
                event['location'] = spans[1].text.strip()
        
        # Extract title, URL, and image
        detail = event_div.find('div', class_='event-result-detail')
        if detail:
            link = detail.find('a')
            if link:
                event['title'] = link.find('h2', class_='event-title').text.strip()
                event['url'] = link['href'].lstrip('/')
                img = link.find('img')
                if img:
                    event['image_url'] = img['src'].lstrip('/')
        
        # Extract subtitle and speaker
        subtitle = detail.find('p', class_='event-subtitle')
        if subtitle:
            event['subtitle'] = subtitle.text.strip()
        
        speaker = detail.find('p', class_='event-speaker')
        if speaker:
            event['speaker'] = speaker.text.strip()
        
        # Extract description
        description = detail.find('div', class_='post-excerpt')
        if description:
            event['description'] = description.text.strip()
        
        # Check if RSVP is required
        rsvp = detail.find('a', class_='eventRsvp')
        if rsvp:
            event['rsvp_required'] = True
        
        events.append(event)
    
    return events

def parse_isaw_events(events):
    standardized_events = []

    for event in events:
        try:
            # Parse date and time
            date_time = datetime.strptime(event['datetime'], "%m/%d/%Y %I:%M %p")
            
            # Assume events are 2 hours long if no end time is provided
            end_time = date_time + timedelta(hours=2)

            # Get location details
            location_str = event.get('location', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Create event ID using hash of URL and title
            event_id = f"evt_isaw_{hashlib.md5((event.get('url', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Build description
            description = event.get('description', '')
            if event.get('subtitle'):
                description = f"{event['subtitle']}\n\n{description}"
            if event.get('speaker'):
                description = f"Speaker: {event['speaker']}\n\n{description}"

            # Create event data for type and category determination
            event_data = {
                "title": event.get('title', ''),
                "description": description,
                "subtitle": event.get('subtitle', '')
            }

            # Create metadata
            metadata = {
                "source_url": event.get('url', ''),
                "source_name": "ISAW Events Calendar",
                "venue": venue,
                "organizer": {
                    "name": "Institute for the Study of the Ancient World",
                    "type": "organizer"
                },
                "additional_info": {
                    "image_url": event.get('image_url', ''),
                    "speaker": event.get('speaker', ''),
                    "subtitle": event.get('subtitle', ''),
                    "rsvp_required": event.get('rsvp_required', False)
                }
            }

            standardized_event = {
                "id": event_id,
                "name": event.get('title', ''),
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_isaw",
                "description": description.strip(),
                "start_date": date_time.isoformat(),
                "end_date": end_time.isoformat(),
                "category": determine_categories(event_data),
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('title', 'Unknown')}. Error: {str(e)}")
            continue

    return {"events": standardized_events}

def scrape_isaw_events():
    raw_events = fetch_isaw_events()
    return parse_isaw_events(raw_events)

def main():
    events = scrape_isaw_events()
    print(f"Successfully processed {len(events['events'])} ISAW events.")
    
    # Save to file for debugging
    if events['events']:
        with open('isaw_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to isaw_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()