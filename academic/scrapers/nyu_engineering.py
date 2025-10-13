import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import hashlib
from event_filter import filter_events, get_filter_stats

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str or location_str == "NYU Engineering":
        return "loc_nyu_tandon"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Default to Tandon campus
    return "loc_nyu_tandon"

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str or location_str == "NYU Engineering":
        return {
            "name": "NYU Tandon School of Engineering",
            "address": "6 MetroTech Center, Brooklyn, NY 11201",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Default case - just clean up the location string
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on event type and title."""
    event_type = event_data.get('type', '').lower()
    title = event_data.get('title', '').lower()
    
    if any(term in event_type + title for term in ['seminar', 'colloquium', 'lecture']):
        return "Seminar"
    elif any(term in event_type + title for term in ['workshop', 'training']):
        return "Workshop"
    elif any(term in event_type + title for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in event_type + title for term in ['career', 'job', 'networking']):
        return "Career"
    elif any(term in event_type + title for term in ['social', 'celebration', 'party']):
        return "Social"
    
    return "Academic"

def determine_categories(event_data):
    """Map Engineering categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    event_type = event_data.get('type', '').lower()
    
    # Default category for Engineering events
    categories.add('TECH')
    
    # Add additional categories based on content
    if any(term in title + event_type for term in ['research', 'science', 'engineering']):
        categories.add('SCIENCE')
    if any(term in title + event_type for term in ['career', 'industry', 'professional']):
        categories.add('CAREER')
    if any(term in title + event_type for term in ['social', 'networking', 'community']):
        categories.add('SOCIAL')
    if any(term in title + event_type for term in ['education', 'learning', 'academic']):
        categories.add('EDUCATION')
    
    return list(categories)

def fetch_nyu_engineering_events(num_pages=4):
    base_url = "https://engineering.nyu.edu/events"
    events = []

    headers = {
        'User-Agent': 'NYUEngineeringEventScraper/1.0 (https://github.com/yourusername/your-repo; youremail@example.com)'
    }

    for page in range(num_pages):
        url = f"{base_url}?event_type=All&department=All&date=All&search=&page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article', class_='node--type-event')
        
        for article in articles:
            event = {}

            # Extract date and time
            date_div = article.find('div', class_='event-teaser-date')
            if date_div:
                month_day = date_div.find('div', class_='month-day').text.strip()
                day_time = date_div.find('div', class_='day-time').text.strip()
                event['date'] = f"{month_day} {datetime.now().year}, {day_time}"

            # Extract title and URL
            title_elem = article.find('h3', class_='h4 link mb-0 mb-sm-3')
            if title_elem and title_elem.a:
                event['title'] = title_elem.a.text.strip()
                event['url'] = f"https://engineering.nyu.edu{title_elem.a['href']}"

            # Extract event type
            event_type_div = article.find('div', class_='field--name-field-event-type')
            if event_type_div:
                event['type'] = event_type_div.text.strip()

            # Extract image URL if present
            img_elem = article.find('img')
            if img_elem and 'src' in img_elem.attrs:
                event['image_url'] = f"https://engineering.nyu.edu{img_elem['src']}"
            else:
                event['image_url'] = None

            events.append(event)

    return events

def parse_nyu_engineering_events(events):
    standardized_events = []

    for event in events:
        try:
            # Parse date and time
            date_str = event['date']
            
            # Split the date string into its components
            date_parts = date_str.split(', ')
            if len(date_parts) != 3:
                # Check if it's a multi-day event
                if ' - ' in date_parts[0]:
                    # For multi-day events, use the start date
                    start_date_str = date_parts[0].split(' - ')[0]
                    time_str = date_parts[1].split(' - ')[0].strip()  # Use the start time
                    date_time_str = f"{start_date_str} {time_str}"
                else:
                    print(f"Unexpected date format: {date_str}")
                    continue
            else:
                date_time_str = f"{date_parts[0]} {date_parts[2]}"
            
            try:
                # Try parsing with full year included
                date_time = datetime.strptime(date_time_str, "%m/%d %Y %I:%M %p")
            except ValueError:
                try:
                    # Try parsing without year, then add current year
                    date_time = datetime.strptime(date_time_str, "%m/%d %I:%M %p")
                    date_time = date_time.replace(year=datetime.now().year)
                except ValueError as e:
                    print(f"Could not parse date string: {date_time_str}. Error: {str(e)}")
                    continue
            
            # Assume events last 1 hour if no end time provided
            end_time = date_time + timedelta(hours=1)

            # Get location details
            location_id = get_location_id("NYU Engineering")
            venue = standardize_venue("NYU Engineering")

            # Create event ID using hash of URL and title
            event_id = f"evt_nyu_eng_{hashlib.md5((event.get('url', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Create metadata
            metadata = {
                "source_url": event.get('url', ''),
                "source_name": "NYU Tandon School of Engineering",
                "venue": venue,
                "organizer": {
                    "name": "NYU Tandon School of Engineering",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": "Tandon School of Engineering",
                    "event_type": event.get('type', ''),
                    "image_url": event.get('image_url')
                }
            }

            standardized_event = {
                "id": event_id,
                "name": event.get('title', ''),
                "type": determine_event_type(event),
                "location_id": location_id,
                "community_id": "com_nyu_tandon",
                "description": "",  # No description available in the source
                "start_date": date_time.isoformat(),
                "end_date": end_time.isoformat(),
                "category": determine_categories(event),
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('title', 'Unknown event')}. Error: {str(e)}")
            continue

    return standardized_events

def scrape_nyu_engineering_events(num_pages=4):
    raw_events = fetch_nyu_engineering_events(num_pages)
    if not raw_events:
        print("No events were found. The website structure might have changed.")
        return {"events": []}
    
    standardized_events = parse_nyu_engineering_events(raw_events)
        # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")

    return {"events": filtered_events}

def main():
    events = scrape_nyu_engineering_events()
    print(f"Successfully processed {len(events['events'])} NYU Engineering events.")
    
    # Save to file for debugging
    if events['events']:
        with open('nyu_engineering_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to nyu_engineering_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()