import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import hashlib

# Add a custom header
headers = {
    'User-Agent': 'JTSAEventScraper/1.0 (https://github.com/yourusername/your-repo; youremail@example.com)'
}

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_jtsa_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific JTSA venues
    if 'library' in location_str:
        return "loc_jtsa_library"
    if 'auditorium' in location_str:
        return "loc_jtsa_auditorium"
    if 'synagogue' in location_str:
        return "loc_jtsa_synagogue"
    
    return "loc_jtsa_main"  # Default to main building

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "Jewish Theological Seminary",
            "address": "3080 Broadway, New York, NY 10027",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle specific JTSA venues
    if 'library' in location_str.lower():
        return {
            "name": "JTS Library",
            "address": "3080 Broadway, New York, NY 10027",
            "type": "venue"
        }
    
    if 'auditorium' in location_str.lower():
        return {
            "name": "JTS Auditorium",
            "address": "3080 Broadway, New York, NY 10027",
            "type": "venue"
        }
    
    if 'synagogue' in location_str.lower():
        return {
            "name": "JTS Synagogue",
            "address": "3080 Broadway, New York, NY 10027",
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
    event_type = event_data.get('type', '').lower()
    
    if any(term in title + ' ' + description + ' ' + event_type for term in ['lecture', 'talk', 'discussion']):
        return "Seminar"
    elif any(term in title + ' ' + description + ' ' + event_type for term in ['workshop', 'class']):
        return "Workshop"
    elif any(term in title + ' ' + description + ' ' + event_type for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + ' ' + description + ' ' + event_type for term in ['service', 'prayer', 'shabbat']):
        return "Religious"
    elif any(term in title + ' ' + description + ' ' + event_type for term in ['performance', 'concert', 'music']):
        return "Performance"
    
    return "Academic"  # Default type

def determine_categories(event_data):
    """Map JTSA categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    
    # Add categories based on content
    if any(term in title + ' ' + description for term in ['torah', 'talmud', 'jewish', 'judaism', 'religious']):
        categories.add('RELIGION')
    if any(term in title + ' ' + description for term in ['history', 'historical', 'archive']):
        categories.add('HISTORY')
    if any(term in title + ' ' + description for term in ['art', 'music', 'culture']):
        categories.add('ARTS')
    if any(term in title + ' ' + description for term in ['education', 'learning', 'study']):
        categories.add('EDUCATION')
    if any(term in title + ' ' + description for term in ['community', 'social']):
        categories.add('SOCIAL')
    
    # If no specific category found, use RELIGION as default
    if not categories:
        categories.add('RELIGION')
    
    return list(categories)

def fetch_jtsa_events(num_pages=2):
    base_url = "https://www.jtsa.edu/events-calendar/"
    events = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}page/{page}/" if page > 1 else base_url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        event_items = soup.find_all('div', class_='standard-list--events')

        for item in event_items:
            event = {}

            # Extract date
            date_box = item.find('div', class_='date-box')
            if date_box:
                month = date_box.find('span', class_='date-box__month').text.strip()
                day = date_box.find('span', class_='date-box__day').text.strip()
                event['date'] = f"{month} {day}"

            # Extract title and URL
            title_elem = item.find('h3', class_='standard-list__title').find('a')
            if title_elem:
                event['title'] = title_elem.text.strip()
                event['url'] = title_elem['href']

            # Extract location and event type
            via_elem = item.find('p', class_='standard-list__via')
            if via_elem:
                event['location'] = via_elem.find('strong').text.strip()
                event['type'] = via_elem.text.split('|')[-1].strip()

            # Extract description
            desc_elem = item.find('p', class_='standard-list__via').find_next_sibling('p')
            if desc_elem:
                event['description'] = desc_elem.text.strip()

            events.append(event)

    return events

def parse_jtsa_events(events):
    standardized_events = []
    current_year = datetime.now().year
    month_abbr = {
        'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
        'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
        'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
    }

    for event in events:
        try:
            # Parse date
            date_str = event['date']
            month, day = date_str.split()
            month = month_abbr.get(month, month)
            date_str = f"{month} {day}, {current_year}"
            
            date = datetime.strptime(date_str, "%B %d, %Y")
            
            # If the parsed date is in the past, assume it's for next year
            if date < datetime.now():
                date = date.replace(year=current_year + 1)
            
            # Default to noon if no time provided
            start_datetime = date.replace(hour=12)
            end_datetime = start_datetime + timedelta(hours=1)

            # Get location details
            location_str = event.get('location', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Create event ID using hash of URL and title
            event_id = f"evt_jtsa_{hashlib.md5((event.get('url', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Create event data for type and category determination
            event_data = {
                "title": event.get('title', ''),
                "description": event.get('description', ''),
                "type": event.get('type', '')
            }

            # Create metadata
            metadata = {
                "source_url": event.get('url', ''),
                "source_name": "JTSA Events Calendar",
                "venue": venue,
                "organizer": {
                    "name": "Jewish Theological Seminary",
                    "type": "organizer"
                }
            }

            standardized_event = {
                "id": event_id,
                "name": event.get('title', ''),
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_jtsa",
                "description": event.get('description', ''),
                "start_date": start_datetime.isoformat(),
                "end_date": end_datetime.isoformat(),
                "category": determine_categories(event_data),
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('title', 'Unknown')}. Error: {str(e)}")
            continue

    return {"events": standardized_events}

def scrape_jtsa_events(num_pages=2):
    raw_events = fetch_jtsa_events(num_pages)
    return parse_jtsa_events(raw_events)

def main():
    events = scrape_jtsa_events()
    print(f"Successfully processed {len(events['events'])} JTSA events.")
    
    # Save to file for debugging
    if events['events']:
        with open('jtsa_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to jtsa_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()