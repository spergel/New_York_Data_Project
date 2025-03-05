import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import hashlib

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_cuny_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific CUNY colleges
    if 'baruch' in location_str:
        return "loc_cuny_baruch"
    if 'hunter' in location_str:
        return "loc_cuny_hunter"
    if 'city college' in location_str or 'ccny' in location_str:
        return "loc_cuny_ccny"
    if 'brooklyn' in location_str:
        return "loc_cuny_brooklyn"
    if 'queens' in location_str:
        return "loc_cuny_queens"
    if 'lehman' in location_str:
        return "loc_cuny_lehman"
    if 'graduate center' in location_str:
        return "loc_cuny_gc"
    
    return "loc_cuny_main"  # Default to main

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "CUNY",
            "address": "205 E 42nd St, New York, NY 10017",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle specific CUNY colleges
    if 'baruch' in location_str.lower():
        return {
            "name": "Baruch College",
            "address": "55 Lexington Ave, New York, NY 10010",
            "type": "venue"
        }
    
    if 'hunter' in location_str.lower():
        return {
            "name": "Hunter College",
            "address": "695 Park Ave, New York, NY 10065",
            "type": "venue"
        }
    
    if 'city college' in location_str.lower() or 'ccny' in location_str.lower():
        return {
            "name": "City College of New York",
            "address": "160 Convent Ave, New York, NY 10031",
            "type": "venue"
        }
    
    if 'brooklyn' in location_str.lower():
        return {
            "name": "Brooklyn College",
            "address": "2900 Bedford Ave, Brooklyn, NY 11210",
            "type": "venue"
        }
    
    if 'queens' in location_str.lower():
        return {
            "name": "Queens College",
            "address": "65-30 Kissena Blvd, Queens, NY 11367",
            "type": "venue"
        }
    
    if 'lehman' in location_str.lower():
        return {
            "name": "Lehman College",
            "address": "250 Bedford Park Blvd W, The Bronx, NY 10468",
            "type": "venue"
        }
    
    if 'graduate center' in location_str.lower():
        return {
            "name": "CUNY Graduate Center",
            "address": "365 5th Ave, New York, NY 10016",
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
    
    if any(term in title + ' ' + description for term in ['lecture', 'talk', 'discussion', 'seminar']):
        return "Seminar"
    elif any(term in title + ' ' + description for term in ['workshop', 'training', 'class']):
        return "Workshop"
    elif any(term in title + ' ' + description for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + ' ' + description for term in ['performance', 'concert', 'theater', 'theatre']):
        return "Performance"
    elif any(term in title + ' ' + description for term in ['exhibition', 'gallery', 'showcase']):
        return "Exhibition"
    
    return "Academic"  # Default type

def determine_categories(event_data):
    """Map CUNY categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    
    # Add categories based on content
    if any(term in title + ' ' + description for term in ['art', 'music', 'performance', 'theatre', 'theater']):
        categories.add('ARTS')
    if any(term in title + ' ' + description for term in ['science', 'technology', 'research', 'stem']):
        categories.add('SCIENCE')
    if any(term in title + ' ' + description for term in ['humanities', 'literature', 'philosophy', 'history']):
        categories.add('HUMANITIES')
    if any(term in title + ' ' + description for term in ['social', 'society', 'community', 'public']):
        categories.add('SOCIAL')
    if any(term in title + ' ' + description for term in ['business', 'economics', 'finance']):
        categories.add('BUSINESS')
    
    # If no specific category found, use EDUCATION as default
    if not categories:
        categories.add('EDUCATION')
    
    return list(categories)

def get_event_details(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    description = (soup.select_one('.cec-event-details p') or 
                   soup.select_one('.eventsDetail__block__text') or 
                   soup.select_one('.tribe-events-single-event-description p'))
    description = description.text.strip() if description else None
    
    date = (soup.select_one('h4:-soup-contains("Date:") + p') or 
            soup.select_one('.eventsDetail__block__details__date') or 
            soup.select_one('.controlholder:-soup-contains("Date:")'))
    date = date.text.strip() if date else None
    
    time = (soup.select_one('h4:-soup-contains("Time:") + p') or 
            soup.select_one('.eventsDetail__block__details__desc__time') or 
            soup.select_one('.controlholder:-soup-contains("Time:")'))
    time = time.text.strip() if time else None
    
    location = (soup.select_one('.eventsDetail__block__details__desc__location') or 
                soup.select_one('.controlholder:-soup-contains("Location:")'))
    location = location.text.strip() if location else None
    
    return {
        'description': description,
        'date': date,
        'time': time,
        'location': location
    }

def fetch_cuny_events(url="https://events.cuny.edu/"):
    events = []
    page = 1
    while url and page <= 4:
        print(f"Processing page {page}")
        page += 1
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        event_items = soup.select('.cec-list-item')
        for item in event_items:
            title = item.select_one('h2 a').text
            link = item.select_one('h2 a')['href']
            date = item.select_one('h4.low-normal').text
            
            details = get_event_details(link)
            
            events.append({
                'title': title,
                'link': link,
                'date': date,
                **details
            })
        
        next_page = soup.select_one('.pagination a:-soup-contains("next")')
        url = next_page['href'] if next_page else None
    
    return events

def parse_cuny_events(events):
    standardized_events = []
    
    for event in events:
        try:
            # Parse date and time
            date_str = event.get('date')
            time_str = event.get('time')
            
            if not date_str:
                print(f"Skipping event due to missing date: {event['title']}")
                continue

            date = datetime.strptime(date_str.replace('\n', '').replace('\r', '').replace(' ', '').replace('Date:', '').replace(',', '').strip(), "%B%d%Y")
            
            if time_str:
                # Assuming time format is like "6:00 PM — 8:30 PM"
                start_time, end_time = time_str.split('—')
                start_datetime = datetime.combine(date.date(), datetime.strptime(start_time.strip(), "%I:%M %p").time())
                end_datetime = datetime.combine(date.date(), datetime.strptime(end_time.strip(), "%I:%M %p").time())
            else:
                start_datetime = date
                end_datetime = date + timedelta(hours=1)  # Assume 1-hour duration if no time provided

            # Get location details
            location_str = event.get('location', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Create event ID using hash of URL and title
            event_id = f"evt_cuny_{hashlib.md5((event.get('link', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Create event data for type and category determination
            event_data = {
                "title": event.get('title', ''),
                "description": event.get('description', '')
            }

            # Create metadata
            metadata = {
                "source_url": event.get('link', ''),
                "source_name": "CUNY Events Calendar",
                "venue": venue,
                "organizer": {
                    "name": "City University of New York",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": event.get('location', '').split('\n')[0] if event.get('location') else ''
                }
            }

            standardized_event = {
                "id": event_id,
                "name": event.get('title', ''),
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_cuny",
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

def scrape_cuny_events():
    raw_events = fetch_cuny_events()
    return parse_cuny_events(raw_events)

def main():
    events = scrape_cuny_events()
    print(f"Successfully processed {len(events['events'])} CUNY events.")
    
    # Save to file for debugging
    if events['events']:
        with open('cuny_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to cuny_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()