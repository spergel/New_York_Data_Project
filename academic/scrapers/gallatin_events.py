import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import hashlib
import re
from event_filter import filter_events, get_filter_stats

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_gallatin_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific Gallatin venues
    if any(term in location_str for term in ['jerry h. labowitz']):
        return "loc_gallatin_labowitz"
    if any(term in location_str for term in ['great room']):
        return "loc_gallatin_greatroom"
    
    return "loc_gallatin_main"  # Default to main building

def parse_address(location_str):
    """Parse address components from location string."""
    if not location_str:
        return None
        
    # Common NYU building addresses
    nyu_buildings = {
        "kimmel": "60 Washington Square South",
        "silver": "31 Washington Place",
        "gallatin": "1 Washington Place"
    }
    
    components = {
        "building_name": "",
        "room": "",
        "street": "",
        "city": "New York",
        "state": "NY",
        "zip": ""
    }
    
    # Clean up the string
    location_str = location_str.replace("-", "-").strip()
    
    # Extract room number if present
    room_patterns = [
        r'Room (\d+[A-Za-z]?)',
        r'(?:^|,\s*)(\d+)(?:\s*(?:st|nd|rd|th)\s*[Ff]loor)',
        r'(?:^|,\s*)(\d+[A-Za-z]?)(?=\s*-|$|\s*,)'
    ]
    
    for pattern in room_patterns:
        match = re.search(pattern, location_str, re.IGNORECASE)
        if match:
            components["room"] = match.group(1)
            # Remove the room number from the string to avoid duplication
            location_str = re.sub(pattern, '', location_str, 1).strip()
            break
    
    # Extract zip code if present
    zip_match = re.search(r'(?:NY|New York)\s*(\d{5})', location_str)
    if zip_match:
        components["zip"] = zip_match.group(1)
        # Remove zip code from string
        location_str = re.sub(r'\s*\d{5}', '', location_str).strip()
    
    # Extract building name and street address
    if "Jerry H. Labowitz Theatre" in location_str:
        components["building_name"] = "Jerry H. Labowitz Theatre for the Performing Arts"
        components["street"] = "1 Washington Place"
        components["zip"] = "10003"
    elif "Gallatin Galleries" in location_str:
        components["building_name"] = "The Gallatin Galleries"
        components["street"] = "1 Washington Place"
        components["zip"] = "10003"
    elif "Kimmel" in location_str:
        components["building_name"] = "Kimmel Center for University Life"
        components["street"] = nyu_buildings["kimmel"]
        components["zip"] = "10012"
    elif "Silver" in location_str:
        components["building_name"] = "The Silver Center for Arts and Science"
        components["street"] = nyu_buildings["silver"]
        components["zip"] = "10003"
    elif "Beacon Theatre" in location_str:
        components["building_name"] = "Beacon Theatre"
        components["street"] = "2124 Broadway"
        components["zip"] = "10023"
    else:
        # Try to extract street address
        street_match = re.search(r'(\d+[^,\n]*(?:Street|St|Avenue|Ave|Place|Pl|Square|Sq|Broadway|Circle|Washington Square South)[^,\n]*)', location_str)
        if street_match:
            components["street"] = street_match.group(1).strip()
            if not components["zip"] and "Washington Place" in components["street"]:
                components["zip"] = "10003"
    
    # Clean up components
    components = {k: v.strip() for k, v in components.items() if v.strip()}
    
    return components

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "NYU Gallatin School",
            "address": "1 Washington Place, New York, NY 10003",
            "type": "venue"
        }
    
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Parse address components
    address_components = parse_address(location_str)
    
    if not address_components:
        return {
            "name": location_str,
            "type": "venue"
        }
    
    # Construct venue object
    venue = {"type": "venue"}
    
    # Set venue name
    if address_components.get("building_name"):
        venue["name"] = address_components["building_name"]
        if address_components.get("room"):
            venue["name"] += f", Room {address_components['room']}"
    else:
        # If no building name but we have a street address, use that
        if address_components.get("street"):
            venue["name"] = address_components["street"]
            if address_components.get("room"):
                venue["name"] = f"Room {address_components['room']}, {venue['name']}"
        else:
            venue["name"] = location_str
    
    # Construct formatted address
    address_parts = []
    
    # Add street address with room if appropriate
    if address_components.get("street"):
        street_part = address_components["street"]
        # Only add room to address if it's not already in the name
        if address_components.get("room") and "Room" not in venue["name"]:
            street_part = f"Room {address_components['room']}, {street_part}"
        address_parts.append(street_part)
    
    # Add city, state, zip
    location_part = "New York, NY"
    if address_components.get("zip"):
        location_part += f" {address_components['zip']}"
    address_parts.append(location_part)
    
    if address_parts:
        venue["address"] = ", ".join(address_parts)
    
    return venue

def determine_event_type(event_data):
    """Determine event type based on title and description."""
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    
    if any(term in title + ' ' + description for term in ['lecture', 'talk', 'discussion']):
        return "Seminar"
    elif any(term in title + ' ' + description for term in ['workshop', 'class']):
        return "Workshop"
    elif any(term in title + ' ' + description for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + ' ' + description for term in ['performance', 'concert', 'theatre', 'theater']):
        return "Performance"
    elif any(term in title + ' ' + description for term in ['exhibition', 'gallery']):
        return "Exhibition"
    
    return "Academic"  # Default type

def determine_categories(event_data):
    """Map Gallatin categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    
    # Add categories based on content
    if any(term in title + ' ' + description for term in ['art', 'performance', 'theatre', 'theater', 'music']):
        categories.add('ARTS')
    if any(term in title + ' ' + description for term in ['humanities', 'literature', 'philosophy']):
        categories.add('HUMANITIES')
    if any(term in title + ' ' + description for term in ['social', 'society', 'community']):
        categories.add('SOCIAL')
    if any(term in title + ' ' + description for term in ['science', 'technology', 'research']):
        categories.add('SCIENCE')
    if any(term in title + ' ' + description for term in ['global', 'international', 'world']):
        categories.add('GLOBAL')
    
    # If no specific category found, use EDUCATION as default
    if not categories:
        categories.add('EDUCATION')
    
    return list(categories)

def parse_single_date(date_str):
    current_year = datetime.now().year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Remove any leading/trailing whitespace and newlines
    date_str = date_str.strip()
    
    parts = date_str.split()
    if len(parts) == 2:  # Month and day
        month, day = parts
        month_num = months.index(month) + 1
        return f"{current_year}-{month_num:02d}-{int(day):02d}"
    elif len(parts) == 3:  # Month, day, and year
        month, day, year = parts
        month_num = months.index(month) + 1
        return f"{year}-{month_num:02d}-{int(day):02d}"
    else:
        raise ValueError(f"Unable to parse date: {date_str}")

def scrape_gallatin_events():
    url = "https://gallatin.nyu.edu/utilities/events.html"
    headers = {
        'User-Agent': 'GallatinEventScraper/1.0 (https://github.com/yourusername/your-repo; youremail@example.com)'
    }
    
    print(f"Fetching events from {url}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return {"events": []}

    print(f"Successfully retrieved page, content length: {len(response.content)}")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Debug: Print the first few characters of the response
    print(f"First 500 chars of response: {response.text[:500]}")
    
    # Debug: Print number of li elements found
    all_lis = soup.find_all('li', class_='col-xs-12')
    print(f"Found {len(all_lis)} event li elements")
    
    standardized_events = []

    # Find all event items - they are in li elements with specific classes
    for event_li in soup.find_all('li', class_='col-xs-12'):
        try:
            # Extract basic event info
            title_elem = event_li.find('h3', class_='event-title')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            url = "https://gallatin.nyu.edu" + event_li.find('a')['href'] if event_li.find('a') else ''
            location = event_li.find('span', class_='event-location')
            location_str = location.text.strip() if location else ''
            
            # Extract date and time
            time_span = event_li.find('span', class_='event-time')
            if not time_span:
                continue
                
            time_text = time_span.text.strip()
            
            # Handle date ranges and times
            date_parts = time_text.split('|')
            if len(date_parts) != 2:
                continue
                
            date_str = date_parts[0].strip()
            time_str = date_parts[1].strip()
            
            # Handle date ranges (e.g., "Apr 14-Apr 18")
            if '-' in date_str:
                start_date, end_date = date_str.split('-')
                parsed_date = parse_single_date(start_date.strip())  # Use start date for single event
            else:
                parsed_date = parse_single_date(date_str)
            
            # Parse time
            if time_str == 'TBD':
                # For TBD times, set a default time range
                start_datetime = datetime.combine(datetime.strptime(parsed_date, "%Y-%m-%d"), datetime.strptime("09:00 AM", "%I:%M %p").time())
                end_datetime = start_datetime + timedelta(hours=1)
            else:
                time_parts = time_str.split('-')
                if len(time_parts) == 2:  # Time range like "7:00 PM-9:30 PM"
                    start_time = datetime.strptime(time_parts[0].strip(), "%I:%M %p").time()
                    end_time = datetime.strptime(time_parts[1].strip(), "%I:%M %p").time()
                    start_datetime = datetime.combine(datetime.strptime(parsed_date, "%Y-%m-%d"), start_time)
                    end_datetime = datetime.combine(datetime.strptime(parsed_date, "%Y-%m-%d"), end_time)
                else:  # Single time like "7:00 PM"
                    time = datetime.strptime(time_str.strip(), "%I:%M %p").time()
                    start_datetime = datetime.combine(datetime.strptime(parsed_date, "%Y-%m-%d"), time)
                    end_datetime = start_datetime + timedelta(hours=1)

            # Get location details
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Create event ID using hash of URL and title
            event_id = f"evt_gallatin_{hashlib.md5((url + title).encode()).hexdigest()[:8]}"

            # Extract image URL
            img_div = event_li.find('div', class_='event-image')
            image_url = ''
            if img_div and 'style' in img_div.attrs:
                style = img_div['style']
                url_start = style.find('url(') + 4
                url_end = style.find(')', url_start)
                image_url = "https://gallatin.nyu.edu" + style[url_start:url_end]

            # Check if RSVP is required
            description = "RSVP required" if event_li.find('span', class_='event-rsvp') else ""

            # Create event data for type and category determination
            event_data = {
                "title": title,
                "description": description
            }

            # Create metadata
            metadata = {
                "source_url": url,
                "source_name": "NYU Gallatin Events",
                "venue": venue,
                "organizer": {
                    "name": "NYU Gallatin School of Individualized Study",
                    "type": "organizer"
                },
                "additional_info": {
                    "image_url": image_url,
                    "rsvp_required": bool(event_li.find('span', class_='event-rsvp'))
                }
            }

            standardized_event = {
                "id": event_id,
                "name": title,
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_gallatin",
                "description": description,
                "start_date": start_datetime.isoformat(),
                "end_date": end_datetime.isoformat(),
                "category": determine_categories(event_data),
                "source": "gallatin",
                "source_group": "NYU",
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {title if 'title' in locals() else 'Unknown'}. Error: {str(e)}")
            continue

        # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")

    return {"events": filtered_events}

def main():
    events = scrape_gallatin_events()
    print(f"Successfully processed {len(events['events'])} Gallatin events.")
    
    # Save to file for debugging
    if events['events']:
        with open('gallatin_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to gallatin_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()