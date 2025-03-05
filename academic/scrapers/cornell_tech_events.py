import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import pytz
import hashlib

# Add a custom header
headers = {
    'User-Agent': 'CornellTechEventScraper/1.0 (https://github.com/yourusername/your-repo; youremail@example.com)'
}

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_cornell_tech_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific Cornell Tech venues
    if 'bloomberg' in location_str:
        return "loc_cornell_tech_bloomberg"
    if 'tata' in location_str:
        return "loc_cornell_tech_tata"
    if 'verizon' in location_str:
        return "loc_cornell_tech_verizon"
    if 'lecture hall' in location_str:
        return "loc_cornell_tech_lecture"
    
    return "loc_cornell_tech_main"  # Default to main building

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "Cornell Tech",
            "address": "2 West Loop Rd, New York, NY 10044",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle specific Cornell Tech venues
    if 'bloomberg' in location_str.lower():
        return {
            "name": "Bloomberg Center",
            "address": "2 West Loop Rd, New York, NY 10044",
            "type": "venue"
        }
    
    if 'tata' in location_str.lower():
        return {
            "name": "Tata Innovation Center",
            "address": "11 E Loop Rd, New York, NY 10044",
            "type": "venue"
        }
    
    if 'verizon' in location_str.lower():
        return {
            "name": "Verizon Executive Education Center",
            "address": "2 West Loop Rd, New York, NY 10044",
            "type": "venue"
        }
    
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title, description, and tags."""
    title = event_data.get('title', '').lower()
    tags = [tag.lower() for tag in event_data.get('tags', [])]
    
    if any(term in title + ' ' + ' '.join(tags) for term in ['lecture', 'talk', 'discussion', 'seminar']):
        return "Seminar"
    elif any(term in title + ' ' + ' '.join(tags) for term in ['workshop', 'training', 'class']):
        return "Workshop"
    elif any(term in title + ' ' + ' '.join(tags) for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + ' ' + ' '.join(tags) for term in ['performance', 'concert', 'show']):
        return "Performance"
    elif any(term in title + ' ' + ' '.join(tags) for term in ['exhibition', 'showcase']):
        return "Exhibition"
    
    return "Academic"  # Default type

def determine_categories(event_data):
    """Map Cornell Tech categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    tags = [tag.lower() for tag in event_data.get('tags', [])]
    
    # Add categories based on content
    if any(term in title + ' ' + ' '.join(tags) for term in ['tech', 'technology', 'digital', 'computing']):
        categories.add('TECH')
    if any(term in title + ' ' + ' '.join(tags) for term in ['business', 'entrepreneurship', 'startup']):
        categories.add('BUSINESS')
    if any(term in title + ' ' + ' '.join(tags) for term in ['research', 'science', 'engineering']):
        categories.add('SCIENCE')
    if any(term in title + ' ' + ' '.join(tags) for term in ['design', 'ux', 'ui', 'product']):
        categories.add('DESIGN')
    if any(term in title + ' ' + ' '.join(tags) for term in ['social', 'society', 'community']):
        categories.add('SOCIAL')
    
    # If no specific category found, use TECH as default for Cornell Tech
    if not categories:
        categories.add('TECH')
    
    return list(categories)

def parse_time_range(time_str):
    # Parse time strings like "10:00 am - 11:00 am"
    start, end = time_str.split(' - ')
    start_time = datetime.strptime(start.strip(), "%I:%M %p")
    end_time = datetime.strptime(end.strip(), "%I:%M %p")
    return start_time, end_time

def scrape_cornell_tech_events(num_pages=5):
    base_url = "https://tech.cornell.edu/events/"
    standardized_events = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}page/{page}/" if page > 1 else base_url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        event_items = soup.find_all('div', class_='event-filter-item')

        for item in event_items:
            try:
                # Extract date
                date_label = item.find('div', class_='event-filter-item__date-label')
                if date_label:
                    day = date_label.find('span', class_='event-filter-item__day').text.strip()
                    month_date = date_label.find('span', class_='event-filter-item__month').text.strip()
                    year = datetime.now().year  # Assume current year if not provided
                    date_str = f"{month_date}, {year}"
                    
                    # Parse the date
                    date = datetime.strptime(f"{date_str} {day}", "%m/%d, %Y %a")

                # Extract title and URL
                title_elem = item.find('a', class_='event-filter-item__title')
                if title_elem:
                    title = title_elem.text.strip()
                    url = title_elem['href']

                # Extract time and location
                time_elem = item.find('div', class_='event-filter-item__open-close-hour')
                location_elem = item.find('div', class_='event-filter-item__where')
                
                if time_elem:
                    time_str = time_elem.text.strip()
                    start_time, end_time = parse_time_range(time_str)
                    start_datetime = date.replace(hour=start_time.hour, minute=start_time.minute)
                    end_datetime = date.replace(hour=end_time.hour, minute=end_time.minute)
                else:
                    start_datetime = date
                    end_datetime = date + timedelta(hours=1)

                location = location_elem.text.strip() if location_elem else ''

                # Extract event types and tags
                tags_elem = item.find('span', class_='event-filter-item__meta-tags')
                tags = [tag.text.strip() for tag in tags_elem.find_all('span', class_='event-filter-item__meta-tags-trigger')] if tags_elem else []

                # Extract image URL
                img_elem = item.find('img', class_='image__img')
                image_url = img_elem['data-normal'] if img_elem and 'data-normal' in img_elem.attrs else None

                # Get location details
                location_id = get_location_id(location)
                venue = standardize_venue(location)

                # Create event ID using hash of URL and title
                event_id = f"evt_cornell_tech_{hashlib.md5((url + title).encode()).hexdigest()[:8]}"

                # Create event data for type and category determination
                event_data = {
                    "title": title,
                    "tags": tags
                }

                # Create metadata
                metadata = {
                    "source_url": url,
                    "source_name": "Cornell Tech Events",
                    "venue": venue,
                    "organizer": {
                        "name": "Cornell Tech",
                        "type": "organizer"
                    },
                    "additional_info": {
                        "image_url": image_url,
                        "tags": tags
                    }
                }

                standardized_event = {
                    "id": event_id,
                    "name": title,
                    "type": determine_event_type(event_data),
                    "location_id": location_id,
                    "community_id": "com_cornell_tech",
                    "description": ", ".join(tags),
                    "start_date": start_datetime.isoformat(),
                    "end_date": end_datetime.isoformat(),
                    "category": determine_categories(event_data),
                    "metadata": metadata
                }

                standardized_events.append(standardized_event)

            except Exception as e:
                print(f"Error processing event: {title if 'title' in locals() else 'Unknown'}. Error: {str(e)}")
                continue

    return {"events": standardized_events}

def main():
    events = scrape_cornell_tech_events()
    print(f"Successfully processed {len(events['events'])} Cornell Tech events.")
    
    # Save to file for debugging
    if events['events']:
        with open('cornell_tech_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to cornell_tech_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()