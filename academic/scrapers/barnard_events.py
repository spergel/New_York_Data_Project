import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import hashlib

# URL of the Barnard events page
url = "https://barnard.edu/events"

# Add a custom header
headers = {
    'User-Agent': 'BarnardEventScraper/1.0 (https://github.com/yourusername/your-repo; youremail@example.com)'
}

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_barnard_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific Barnard venues
    if 'diana' in location_str:
        return "loc_barnard_diana"
    if 'milbank' in location_str:
        return "loc_barnard_milbank"
    if 'altschul' in location_str:
        return "loc_barnard_altschul"
    if 'barnard hall' in location_str:
        return "loc_barnard_hall"
    if 'liz' in location_str or 'plimpton' in location_str:
        return "loc_barnard_liz"
    
    return "loc_barnard_main"  # Default to main campus

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "Barnard College",
            "address": "3009 Broadway, New York, NY 10027",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle specific Barnard venues
    if 'diana' in location_str.lower():
        return {
            "name": "The Diana Center",
            "address": "3009 Broadway, New York, NY 10027",
            "type": "venue"
        }
    
    if 'milbank' in location_str.lower():
        return {
            "name": "Milbank Hall",
            "address": "3009 Broadway, New York, NY 10027",
            "type": "venue"
        }
    
    if 'altschul' in location_str.lower():
        return {
            "name": "Altschul Hall",
            "address": "3009 Broadway, New York, NY 10027",
            "type": "venue"
        }
    
    if 'barnard hall' in location_str.lower():
        return {
            "name": "Barnard Hall",
            "address": "3009 Broadway, New York, NY 10027",
            "type": "venue"
        }
    
    if 'liz' in location_str.lower() or 'plimpton' in location_str.lower():
        return {
            "name": "The LeFrak Center",
            "address": "3009 Broadway, New York, NY 10027",
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
    """Map Barnard categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    
    # Add categories based on content
    if any(term in title + ' ' + description for term in ['art', 'music', 'performance', 'theatre', 'theater']):
        categories.add('ARTS')
    if any(term in title + ' ' + description for term in ['science', 'stem', 'research', 'lab']):
        categories.add('SCIENCE')
    if any(term in title + ' ' + description for term in ['humanities', 'literature', 'philosophy', 'history']):
        categories.add('HUMANITIES')
    if any(term in title + ' ' + description for term in ['social', 'society', 'community', 'public']):
        categories.add('SOCIAL')
    if any(term in title + ' ' + description for term in ['women', 'gender', 'feminism', 'equality']):
        categories.add('GENDER')
    
    # If no specific category found, use EDUCATION as default
    if not categories:
        categories.add('EDUCATION')
    
    return list(categories)

def parse_date_time(date_str, time_str):
    try:
        # Parse date
        date = datetime.strptime(date_str, "%A, %B %d, %Y")
        
        # Parse time
        start_time_str, end_time_str = time_str.split(' - ')
        start_time = datetime.strptime(start_time_str, "%I:%M %p").time()
        end_time = datetime.strptime(end_time_str, "%I:%M %p").time()
        
        # Combine date and time
        start_datetime = date.replace(hour=start_time.hour, minute=start_time.minute)
        end_datetime = date.replace(hour=end_time.hour, minute=end_time.minute)
        
        # If end time is earlier than start time, assume it's the next day
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)
        
        return start_datetime, end_datetime
    except ValueError:
        # If parsing fails, return None
        return None

def scrape_barnard_events():
    # Fetch the webpage content
    response = requests.get(url, headers=headers)
    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all event cards
    event_cards = soup.find_all('article', class_='cc--component-container cc--event-card')

    standardized_events = []

    for card in event_cards:
        try:
            # Extract basic event info
            title_elem = card.find('div', class_='f--field f--cta-title')
            if not title_elem or not title_elem.find('a'):
                continue
                
            title = title_elem.find('a').text.strip()
            event_url = "https://barnard.edu" + title_elem.find('a')['href']
            
            # Extract date and time
            date_elem = card.find('div', class_='f--field f--date')
            time_elem = card.find('div', class_='f--field f--time')
            
            if not date_elem:
                continue
                
            date_str = date_elem.text.strip()
            time_str = time_elem.text.strip() if time_elem else "00:00 AM - 11:59 PM"
            
            # Parse date and time
            date_time = parse_date_time(date_str, time_str)
            if not date_time:
                continue
                
            start_time, end_time = date_time

            # Extract location
            location_elem = card.find('div', class_='f--field f--event-location')
            location = location_elem.text.strip() if location_elem else ''

            # Get location details
            location_id = get_location_id(location)
            venue = standardize_venue(location)

            # Create event ID using hash of URL and title
            event_id = f"evt_barnard_{hashlib.md5((event_url + title).encode()).hexdigest()[:8]}"

            # Extract image URL
            img_elem = card.find('img')
            image_url = "https://barnard.edu" + img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''

            # Create event data for type and category determination
            event_data = {
                "title": title,
                "description": ""  # No description available in the card
            }

            # Create metadata
            metadata = {
                "source_url": event_url,
                "source_name": "Barnard Events Calendar",
                "venue": venue,
                "organizer": {
                    "name": "Barnard College",
                    "type": "organizer"
                },
                "additional_info": {
                    "image_url": image_url
                }
            }

            standardized_event = {
                "id": event_id,
                "name": title,
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_barnard",
                "description": "",  # No description available in the card
                "start_date": start_time.isoformat(),
                "end_date": end_time.isoformat(),
                "category": determine_categories(event_data),
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {title if 'title' in locals() else 'Unknown'}. Error: {str(e)}")
            continue

    return {"events": standardized_events}

def main():
    events = scrape_barnard_events()
    print(f"Successfully processed {len(events['events'])} Barnard events.")
    
    # Save to file for debugging
    if events['events']:
        with open('barnard_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to barnard_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()
