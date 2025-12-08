import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re
import time
import hashlib
from event_filter import filter_events, get_filter_stats
from category_utils import determine_categories
from date_utils import standardize_datetime, create_nyc_datetime, NY_TZ

# Add a custom header that mimics a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def clean_text(text):
    """Clean up text by removing extra whitespace and newlines."""
    if not text:
        return ""
    # Replace multiple spaces, newlines, and tabs with a single space
    cleaned = re.sub(r'\s+', ' ', text.strip())
    # Remove spaces before punctuation
    cleaned = re.sub(r'\s+([,.])', r'\1', cleaned)
    return cleaned

def extract_location_and_date(location_text):
    """Extract location and date from combined text."""
    if not location_text:
        return "", ""
    
    # Clean up the text first
    text = clean_text(location_text)
    
    # Try to find the month name in the text
    month_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+'
    match = re.search(month_pattern, text)
    
    if match:
        # Split at the month name
        parts = re.split(f'({month_pattern})', text)
        if len(parts) >= 3:
            location = parts[0].strip().rstrip(',')
            date = f"{parts[1]}, 2025"  # Add the year since it's not in the location string
            return location, date
    
    return text, ""

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return None
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for Warren Weaver Hall
    if 'warren weaver' in location_str or 'wwh' in location_str:
        return "loc_nyu_wwh"
    
    # Check for 60 Fifth Avenue
    if '60 fifth' in location_str:
        return "loc_nyu_60fifth"
    
    # Default to main campus
    return "loc_nyu_main"

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
    
    # Handle Warren Weaver Hall
    if 'warren weaver' in location_str.lower() or 'wwh' in location_str.lower():
        name = f"Warren Weaver Hall{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "251 Mercer St, New York, NY 10012",
            "type": "venue"
        }
    
    # Handle 60 Fifth Avenue
    if '60 fifth' in location_str.lower():
        name = f"60 Fifth Avenue{f', Room {room_number}' if room_number else ''}"
        return {
            "name": name,
            "address": "60 Fifth Avenue, New York, NY 10011",
            "type": "venue"
        }
    
    # Default case - just clean up the location string
    return {
        "name": clean_text(location_str),
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title and description."""
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    
    if any(term in title for term in ['seminar', 'colloquium', 'lecture']):
        return "Seminar"
    elif any(term in title for term in ['workshop', 'training']):
        return "Workshop"
    elif any(term in title for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in description for term in ['thesis', 'dissertation', 'defense']):
        return "Defense"
    
    return "Academic"

def determine_categories_cims(event_data):
    """Determine categories for CIMS events using centralized logic."""
    # Use the centralized categorization with keyword analysis
    categories = determine_categories(event_data, method='auto')

    # Ensure CIMS events get SCIENCE category (they're math/computation focused)
    if 'SCIENCE' not in categories:
        categories.append('SCIENCE')

    return categories

def fetch_cims_events(num_pages=2):
    """Fetch events from the CIMS website."""
    base_url = "https://cims.nyu.edu/dynamic/events/"
    events = []

    for page in range(1, num_pages + 1):
        try:
            url = f"{base_url}?page={page}" if page > 1 else base_url
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Add a small delay between requests
            time.sleep(1)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # First try the new structure
            event_items = soup.find_all('div', class_='event-item')
            if not event_items:
                # Try alternative class names
                event_items = soup.find_all(['div', 'li'], class_=['d-flex flex-column', 'event-listing'])

            if not event_items:
                print(f"Warning: No events found on page {page}")
                continue

            for item in event_items:
                event = {}
                
                # Try multiple possible class names for title
                title_elem = (item.find(['h3', 'h2', 'div'], class_=['event-title', 'event-name', 'title']) or
                            item.find('a', class_='event-link'))
                
                if title_elem:
                    if title_elem.find('a'):
                        title_elem = title_elem.find('a')
                    event['title'] = clean_text(title_elem.text)
                    # Get URL if it exists
                    url_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                    if url_elem and 'href' in url_elem.attrs:
                        event['url'] = f"https://cims.nyu.edu{url_elem['href']}" if not url_elem['href'].startswith('http') else url_elem['href']

                # Try multiple possible class names for location
                location_elem = item.find(['div', 'span'], class_=['event-location', 'location'])
                if location_elem:
                    location_text = location_elem.text
                    location, date = extract_location_and_date(location_text)
                    event['location'] = location
                    if date:
                        event['date_time'] = date
                
                # Try to find date/time if not already found
                if 'date_time' not in event:
                    date_elem = item.find(['div', 'span'], class_=['event-date', 'date'])
                    if date_elem:
                        event['date_time'] = clean_text(date_elem.text)

                # Extract speaker information
                speaker_elem = item.find(['div', 'span'], class_=['event-speaker', 'speaker'])
                if speaker_elem:
                    # Handle multiple speakers
                    speaker_text = speaker_elem.text
                    # Replace "and" with comma for consistent splitting
                    speaker_text = re.sub(r'\s+and\s+', ', ', speaker_text)
                    speakers = [clean_text(s) for s in speaker_text.split(',') if clean_text(s)]
                    event['speaker'] = ', '.join(speakers)

                # Extract description/synopsis
                desc_elem = item.find(['div', 'p'], class_=['event-synopsis', 'description'])
                if desc_elem:
                    event['description'] = clean_text(desc_elem.text)

                if event:  # Only append if we found some information
                    events.append(event)

        except requests.RequestException as e:
            print(f"Error fetching page {page}: {str(e)}")
            continue
        except Exception as e:
            print(f"Unexpected error on page {page}: {str(e)}")
            continue

    return events

def parse_cims_events(events):
    """Parse and standardize CIMS events."""
    standardized_events = []

    for event in events:
        try:
            if 'date_time' not in event:
                print(f"Skipping event without date/time: {event.get('title', 'Unknown event')}")
                continue

            # Clean up date_time string
            date_time_str = event['date_time'].replace('\n', ' ').strip()
            
            # Parse the date string that includes month name
            date_match = re.match(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d+),\s*(\d{4})', date_time_str)
            if not date_match:
                print(f"Could not parse date string: {date_time_str}")
                continue
            
            month_str, day_str, year_str = date_match.groups()
            
            # Convert month name to number
            month = datetime.strptime(month_str, "%B").month
            day = int(day_str)
            year = int(year_str)
            
            # Default to 2:00 PM if no time is specified
            time = datetime.strptime("14:00", "%H:%M").time()
            
            # Create the datetime objects
            start_date = datetime.combine(datetime(year, month, day), time)
            end_date = start_date + timedelta(hours=1)  # Assume 1-hour events if no end time specified

            # Get location details
            location_str = event.get('location', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Create event ID using hash of URL and title
            event_id = f"evt_nyu_cims_{hashlib.md5((event.get('url', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Create metadata
            metadata = {
                "source_url": event.get('url', ''),
                "source_name": "NYU Courant Institute",
                "venue": venue,
                "organizer": {
                    "name": "NYU Courant Institute",
                    "type": "organizer"
                },
                "additional_info": {
                    "speaker": event.get('speaker', ''),
                    "department": "Courant Institute of Mathematical Sciences",
                    "tags": ["mathematics", "computer science", "research"]
                }
            }

            # Use speaker as title if available, otherwise fall back to original title
            event_title = event.get('speaker', '') if event.get('speaker') else event.get('title', '')
            
            standardized_event = {
                "id": event_id,
                "name": event_title,
                "type": determine_event_type(event),
                "location_id": location_id,
                "community_id": "com_nyu_courant",
                "description": event.get('description', ''),
                "start_date": standardize_datetime(start_date),
                "end_date": standardize_datetime(end_date),
                "category": determine_categories_cims(event),
                "source": "nyu_cims",
                "source_group": "nyu_cims",
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('title', 'Unknown event')}. Error: {str(e)}")
            continue

    return standardized_events

def scrape_cims_events(num_pages=2):
    """Main function to scrape and process CIMS events."""
    raw_events = fetch_cims_events(num_pages)
    if not raw_events:
        print("No events were found. The website structure might have changed.")
        return {"events": []}
    
    standardized_events = parse_cims_events(raw_events)
        # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")

    return {"events": filtered_events}

def main():
    events = scrape_cims_events()
    print(f"Successfully processed {len(events['events'])} CIMS events.")
    
    # Save to file for debugging
    if events['events']:
        with open('cims_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to cims_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()