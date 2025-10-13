import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import hashlib
from event_filter import filter_events, get_filter_stats

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_virtual"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for Sof Heyman Center
    if any(term in location_str for term in ['sof heyman', 'heyman center']):
        return "loc_columbia_heyman"
    
    return "loc_columbia_main"  # Default to Columbia main campus

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str or any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle Sof Heyman Center
    if any(term in location_str.lower() for term in ['sof heyman', 'heyman center']):
        return {
            "name": "Heyman Center for the Humanities",
            "address": "74 Morningside Dr, New York, NY 10027",
            "type": "venue"
        }
    
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title and categories."""
    title = event_data.get('title', '').lower()
    categories = [cat.lower() for cat in event_data.get('categories', [])]
    description = event_data.get('description', '').lower()
    
    if any(term in title + ' '.join(categories) for term in ['seminar', 'colloquium', 'lecture']):
        return "Seminar"
    elif any(term in title + ' '.join(categories) for term in ['workshop', 'training']):
        return "Workshop"
    elif any(term in title + ' '.join(categories) for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + ' '.join(categories) for term in ['reading', 'book talk']):
        return "Reading"
    elif any(term in description for term in ['thesis', 'dissertation', 'defense']):
        return "Defense"
    
    return "Academic"

def determine_categories(event_data):
    """Map Sof Heyman categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    event_categories = [cat.lower() for cat in event_data.get('categories', [])]
    description = event_data.get('description', '').lower()
    
    # Default category
    categories.add('HUMANITIES')
    
    # Add categories based on content
    if any(term in title + ' '.join(event_categories) + description for term in ['literature', 'poetry', 'writing']):
        categories.add('LITERATURE')
    if any(term in title + ' '.join(event_categories) + description for term in ['history', 'historical']):
        categories.add('HISTORY')
    if any(term in title + ' '.join(event_categories) + description for term in ['philosophy', 'ethics']):
        categories.add('PHILOSOPHY')
    if any(term in title + ' '.join(event_categories) + description for term in ['art', 'culture', 'museum']):
        categories.add('ARTS')
    if any(term in title + ' '.join(event_categories) + description for term in ['social', 'society', 'community']):
        categories.add('SOCIAL')
    
    return list(categories)

def parse_date(date_str):
    # Remove any whitespace and split by dash if it's a range
    date_parts = [part.strip() for part in date_str.split('–')]
    
    def parse_single_date(date):
        # Try parsing with day
        try:
            return datetime.strptime(date, "%B %d, %Y")
        except ValueError:
            # If fails, try parsing without day
            try:
                return datetime.strptime(date, "%B %Y")
            except ValueError:
                # If both fail, return None
                return None

    # Parse the first date (start date)
    start_date = parse_single_date(date_parts[0])
    
    # If it's a range, parse the end date
    if len(date_parts) > 1:
        # Check if the second part has a year, if not, use the year from the first part
        if not re.search(r'\d{4}', date_parts[1]):
            year = re.search(r'\d{4}', date_parts[0]).group()
            date_parts[1] += f", {year}"
        end_date = parse_single_date(date_parts[1])
    else:
        end_date = start_date

    return start_date, end_date

def fetch_sofheyman_events():
    url = "https://sofheyman.org/events/upcoming"
    scraper = cloudscraper.create_scraper(delay=10)  # delay set to 10 seconds
    
    try:
        response = scraper.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to retrieve the page. Error: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    events = []
    
    for event_div in soup.find_all('div', class_='grid-box'):
        event = {}
        
        # Extract date
        date_span = event_div.find('span', class_='date')
        if date_span:
            event['date'] = date_span.string.strip()
        
        # Extract title and URL
        title_link = event_div.find('h3').find('a') if event_div.find('h3') else event_div.find('h4').find('a') if event_div.find('h4') else None
        if title_link:
            event['title'] = title_link.string.strip()
            event['url'] = "https://sofheyman.org" + title_link['href']
        
        # Extract categories
        categories = event_div.find('div', class_='category')
        if categories:
            event['categories'] = [a.string.strip() for a in categories.find_all('a')]
        
        # Extract image URL
        img_tag = event_div.find('img')
        if img_tag and 'src' in img_tag.attrs:
            event['image_url'] = img_tag['src']
        
        # Extract description
        description = event_div.find('p')
        if description:
            event['description'] = description.string.strip()
        
        # Extract time and location
        meta_div = event_div.find('div', class_='meta')
        if meta_div:
            time_span = meta_div.find('span', string=lambda t: t and 'EDT' in t)
            if time_span:
                event['time'] = time_span.string.strip()
            location_a = meta_div.find('a', href='/connect/visit')
            if location_a:
                event['location'] = location_a.string.strip()
        
        events.append(event)

    return events

def parse_sofheyman_events(events):
    standardized_events = []

    for event in events:
        try:
            start_date, end_date = parse_date(event['date'])
            
            if start_date is None:
                print(f"Error parsing date for event: {event['title']}")
                continue

            # Parse time if available
            if 'time' in event:
                time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)', event['time'])
                if time_match:
                    time_str = time_match.group(1)
                    time = datetime.strptime(time_str, "%I:%M %p").time()
                    start_date = datetime.combine(start_date.date(), time)
                    end_date = start_date + timedelta(hours=2)  # Assume 2-hour duration if no end time
                else:
                    end_date = start_date + timedelta(days=1)  # Assume full-day event if no time provided
            else:
                end_date = start_date + timedelta(days=1)  # Assume full-day event if no time provided

            # Get location details
            location_str = event.get('location', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Create event ID using hash of URL and title
            event_id = f"evt_heyman_{hashlib.md5((event.get('url', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Create metadata
            metadata = {
                "source_url": event.get('url', ''),
                "source_name": "Sof Heyman Center",
                "venue": venue,
                "organizer": {
                    "name": "Sof Heyman Center for the Humanities",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": "Heyman Center for the Humanities",
                    "categories": event.get('categories', []),
                    "image_url": event.get('image_url', '')
                }
            }

            standardized_event = {
                "id": event_id,
                "name": event['title'],
                "type": determine_event_type(event),
                "location_id": location_id,
                "community_id": "com_columbia_heyman",
                "description": event.get('description', ''),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "category": determine_categories(event),
                "source": "sof_heyman",
                "source_group": "Independent",
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except KeyError as e:
            print(f"Error parsing event: {event.get('title', 'Unknown')}. Missing key: {str(e)}")
        except ValueError as e:
            print(f"Error parsing event: {event.get('title', 'Unknown')}. Error: {str(e)}")

        # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")

    return {"events": filtered_events}

def scrape_sofheyman_events():
    raw_events = fetch_sofheyman_events()
    return parse_sofheyman_events(raw_events)

def main():
    events = scrape_sofheyman_events()
    print(f"Successfully processed {len(events['events'])} Sof Heyman events.")
    
    # Save to file for debugging
    if events['events']:
        with open('sofheyman_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to sofheyman_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()