import requests
from bs4 import BeautifulSoup
import json
import logging
import hashlib
import os
import sys
import re
import time
from datetime import datetime, timedelta
from dateutil import parser
from typing import Dict, List, Optional, Tuple
import pytz
import random
import traceback
from enum import Enum

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from general.models import Event, EventMetadata, Price, Venue, Organizer, EventCategory, EventStatus

# Import proxy list from separate file
from exercise.scrapers.proxy_list import WEBSHARE_PROXY_LIST, WEBSHARE_USERNAME, WEBSHARE_PASSWORD

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Add file handler to keep logs
os.makedirs('/logs', exist_ok=True)
file_handler = logging.FileHandler('/logs/scraper.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# Set to track blacklisted proxies
blacklisted_proxies = set()

def get_proxy_session() -> Tuple[requests.Session, str]:
    """Get a requests session with a random proxy from the list"""
    
    global blacklisted_proxies
    
    # Create a new session
    session = requests.Session()
    
    # Try to find a non-blacklisted proxy
    available_proxies = [p for p in WEBSHARE_PROXY_LIST if p not in blacklisted_proxies]
    
    # If all proxies are blacklisted, reset the blacklist and use any proxy
    if not available_proxies:
        logging.warning("All proxies are blacklisted! Resetting blacklist.")
        blacklisted_proxies.clear()
        available_proxies = WEBSHARE_PROXY_LIST
    
    # Choose a random proxy
    proxy = random.choice(available_proxies)
    
    # Parse the proxy string which now includes credentials
    if ":" in proxy:
        parts = proxy.split(":")
        if len(parts) == 4:  # Format: ip:port:username:password
            ip, port, username, password = parts
            # Format the proxy URL with authentication
            proxy_url = f"http://{username}:{password}@{ip}:{port}"
        else:  # Old format: ip:port
            # Format the proxy URL with authentication from global variables
            proxy_url = f"http://{WEBSHARE_USERNAME}:{WEBSHARE_PASSWORD}@{proxy}"
    else:
        # Fallback to global credentials
        proxy_url = f"http://{WEBSHARE_USERNAME}:{WEBSHARE_PASSWORD}@{proxy}"
    
    # Set the proxy in the session
    session.proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    # Set a user agent to mimic a real browser
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    
    return session, proxy

def make_request(url: str, max_retries: int = 3) -> Optional[requests.Response]:
    """Make a request to the given URL with retries and proxy rotation"""
    global blacklisted_proxies
    
    used_proxies = set()  # Track proxies that have been used in this request
    
    for attempt in range(1, max_retries + 1):
        session, proxy = get_proxy_session()
        
        # Skip proxies that have already failed in this request
        if proxy in used_proxies:
            logging.info(f"Skipping already used proxy: {proxy}")
            continue
            
        logging.info(f"Attempt {attempt}/{max_retries} with proxy: {proxy}")
        
        try:
            response = session.get(url, timeout=30)
            
            # Check if we got a 403 error
            if response.status_code == 403:
                logging.warning(f"403 Forbidden error with proxy {proxy}. Adding to used and blacklisted proxies.")
                used_proxies.add(proxy)
                blacklisted_proxies.add(proxy)
                continue
                
            # Check if we got a 202 status code (request accepted but processing not completed)
            if response.status_code == 202:
                logging.warning(f"202 Accepted but not completed error with proxy {proxy}. Adding to used and blacklisted proxies.")
                used_proxies.add(proxy)
                blacklisted_proxies.add(proxy)
                continue
                
            # Log successful request
            logging.info(f"Successfully fetched {url} with proxy {proxy}")
            logging.debug(f"Response headers: {response.headers}")
            logging.debug(f"Response preview: {response.text[:200]}...")
            
            return response
            
        except requests.RequestException as e:
            logging.error(f"Request failed with proxy {proxy}: {str(e)}")
            used_proxies.add(proxy)
            
    logging.error(f"All {max_retries} attempts failed for URL: {url}")
    return None

def generate_event_id(name: str, start_date: datetime, venue_name: str) -> str:
    """Generate a unique ID for an event based on its name, date, and venue"""
    unique_string = f"{name}_{start_date.isoformat()}_{venue_name}"
    return f"evt_nycparks_{hashlib.md5(unique_string.encode()).hexdigest()[:8]}"

def parse_date_time(date_str: str, time_str: str) -> tuple:
    """Parse date and time strings into datetime objects"""
    # NYC Parks format: "Thursday, March 6, 2025" and "1:00 p.m.–2:00 p.m."
    try:
        # Parse the date
        date_obj = parser.parse(date_str)
        
        # Parse the time
        # Extract start and end times
        time_parts = time_str.split('–')
        start_time_str = time_parts[0].strip()
        end_time_str = time_parts[1].strip() if len(time_parts) > 1 else start_time_str
        
        # Parse start time
        start_time = parser.parse(start_time_str)
        
        # Parse end time
        end_time = parser.parse(end_time_str)
        
        # Combine date and time
        start_datetime = date_obj.replace(
            hour=start_time.hour,
            minute=start_time.minute,
            second=0,
            microsecond=0
        )
        
        end_datetime = date_obj.replace(
            hour=end_time.hour,
            minute=end_time.minute,
            second=0,
            microsecond=0
        )
        
        # Set timezone to Eastern Time
        eastern = pytz.timezone('US/Eastern')
        start_datetime = eastern.localize(start_datetime)
        end_datetime = eastern.localize(end_datetime)
        
        return start_datetime, end_datetime
    except Exception as e:
        logging.error(f"Error parsing date/time: {date_str} / {time_str} - {str(e)}")
        return None, None

def determine_categories(category_links: List[str]) -> List[EventCategory]:
    """Determine event categories based on category names"""
    category_mapping = {
        "fitness": EventCategory.EXERCISE,
        "shape up nyc": EventCategory.EXERCISE,
        "yoga": EventCategory.EXERCISE,
        "pilates": EventCategory.EXERCISE,
        "dance": EventCategory.EXERCISE,
        "workshops": EventCategory.EDUCATION,
        "community": EventCategory.SOCIAL,
        "arts": EventCategory.ARTS,
        "culture": EventCategory.CULTURE,
        "education": EventCategory.EDUCATION,
        "networking": EventCategory.NETWORKING,
        "social": EventCategory.SOCIAL,
        "science": EventCategory.SCIENCE,
        "tech": EventCategory.TECH,
        "business": EventCategory.BUSINESS,
        "health": EventCategory.HEALTH,
        "exercise classes": EventCategory.EXERCISE,
        "yoga & pilates classes": EventCategory.EXERCISE
    }
    
    categories = []
    for category in category_links:
        category_lower = category.lower()
        matched = False
        
        # Try exact match first
        if category_lower in category_mapping:
            if category_mapping[category_lower] not in categories:
                categories.append(category_mapping[category_lower])
                matched = True
        else:
            # Try partial match
            for key, value in category_mapping.items():
                if key in category_lower and value not in categories:
                    categories.append(value)
                    matched = True
        
        # Log the category mapping
        if matched:
            logging.info(f"Mapped category '{category}' to {[c.value for c in categories]}")
    
    # Default to EXERCISE if no categories matched (since these are NYC Parks fitness events)
    if not categories:
        logging.info(f"No categories matched, defaulting to EXERCISE")
        categories.append(EventCategory.EXERCISE)
    
    return categories

def generate_location_id(venue_name: str) -> str:
    """Generate a unique ID for a location based on its name"""
    return f"loc_nycparks_{hashlib.md5(venue_name.encode()).hexdigest()[:8]}"

def create_location_entry(venue_details: Dict) -> Dict:
    """Create a standardized location entry from venue details"""
    location = {
        "id": generate_location_id(venue_details['name']),
        "name": venue_details['name'],
        "type": "Community Center" if "center" in venue_details['name'].lower() else "Recreation Facility",
        "address": venue_details['address'],
        "city": venue_details['borough'],
        "state": "NY",
        "coordinates": {
            "lat": venue_details['coordinates']['latitude'] if venue_details['coordinates'] else None,
            "lng": venue_details['coordinates']['longitude'] if venue_details['coordinates'] else None
        },
        "description": f"A NYC Parks facility in {venue_details['borough']} offering community programs and events.",
        "amenities": [
            "Event Space",
            "Community Programs"
        ],
        "capacity": "Medium",
        "accessibility": venue_details['accessibility'],
        "website": f"https://www.nycgovparks.org/facilities/{venue_details['name'].lower().replace(' ', '-')}",
        "images": [],
        "hours": {
            "monday": "Varies by program",
            "tuesday": "Varies by program",
            "wednesday": "Varies by program",
            "thursday": "Varies by program",
            "friday": "Varies by program",
            "saturday": "Varies by program",
            "sunday": "Varies by program"
        },
        "eventTypes": [
            "Fitness",
            "Recreation",
            "Community"
        ]
    }
    
    # Clean up None values
    if not location['coordinates']['lat'] or not location['coordinates']['lng']:
        del location['coordinates']
        
    return location

def datetime_serializer(obj):
    """Helper function to serialize datetime objects to ISO format for JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Type {type(obj)} not serializable")

def save_locations(locations: List[Dict]):
    """Save unique locations to a JSON file"""
    output_file = './data/locations.json'
    
    try:
        # Load existing locations if file exists
        existing_locations = {}
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                data = json.load(f)
                existing_locations = {loc.get('id'): loc for loc in data.get('locations', [])}
        
        # Update with new locations
        for location in locations:
            if location.get('id') not in existing_locations:
                logging.info(f"Adding new location: {location.get('name')}")
                existing_locations[location.get('id')] = location
            else:
                # Update existing location with any new information
                logging.info(f"Updating existing location: {location.get('name')}")
                existing = existing_locations[location.get('id')]
                if 'coordinates' in location and 'coordinates' not in existing:
                    existing['coordinates'] = location['coordinates']
                if location.get('accessibility') and not existing.get('accessibility'):
                    existing['accessibility'] = location['accessibility']
        
        # Save updated locations
        with open(output_file, 'w') as f:
            json.dump({"locations": list(existing_locations.values())}, f, indent=4, default=datetime_serializer)
        logging.info(f"Saved {len(existing_locations)} locations to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save locations: {str(e)}")
        logging.error(traceback.format_exc())

def fetch_event_page(event_url: str) -> Optional[BeautifulSoup]:
    """Fetch the HTML content of an event page and return a BeautifulSoup object"""
    global blacklisted_proxies
    
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        logging.info(f"Fetching event page: {event_url} (Attempt {attempt}/{max_attempts})")
        
        response = make_request(event_url)
        
        if not response:
            logging.error(f"Failed to get response for event page: {event_url}")
            time.sleep(5)  # Wait before retry
            continue
            
        # Check for 202 status code (request accepted but processing not completed)
        if response.status_code == 202:
            logging.warning(f"Failed to fetch event page: 202")
            
            # Get the proxy from the session
            proxy_url = response.request.proxies.get('http', '').split('@')[-1]
            if proxy_url:
                logging.warning(f"Blacklisting proxy that received 202 status: {proxy_url}")
                blacklisted_proxies.add(proxy_url)
                
            time.sleep(5)  # Wait before retry
            continue
            
        # Check for 403 error or bot challenge page
        if response.status_code == 403 or "challenge-container" in response.text or "awswaf" in response.text:
            logging.warning(f"403 Forbidden or bot challenge detected for event page: {event_url}")
            
            # Get the proxy from the session
            proxy_url = response.request.proxies.get('http', '').split('@')[-1]
            if proxy_url:
                logging.warning(f"Blacklisting proxy that triggered bot detection: {proxy_url}")
                blacklisted_proxies.add(proxy_url)
                
            time.sleep(5)  # Wait before retry
            continue
            
        # Check if we got a valid response
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if we got a valid event page
            if soup.find('div', class_='single_event') or soup.find('div', id='event'):
                logging.info(f"Successfully fetched event page: {event_url}")
                time.sleep(3)  # Add delay to avoid rate limiting
                return soup
            else:
                logging.warning(f"Response doesn't contain event information: {event_url}")
                logging.debug(f"HTML preview: {response.text[:200]}")
        else:
            logging.warning(f"Unexpected status code: {response.status_code} for {event_url}")
            
        time.sleep(5)  # Wait before retry
    
    logging.error(f"Failed to fetch event page after {max_attempts} attempts: {event_url}")
    return None

def parse_event_from_list(event_div) -> Optional[Dict]:
    """
    Parse basic event information from the event list page.
    """
    try:
        logging.info(f"Parsing event from list")
        
        # Try different HTML structures for event name
        name_elem = None
        
        # Try structure 1: h3 with class 'event_title'
        name_elem = event_div.find('h3', class_='event_title')
        
        # Try structure 2: h4 with class 'event_title'
        if not name_elem:
            name_elem = event_div.find('h4', class_='event_title')
            
        # Try structure 3: div with class 'event_title'
        if not name_elem:
            name_elem = event_div.find('div', class_='event_title')
            
        # Try structure 4: any h3 or h4
        if not name_elem:
            name_elem = event_div.find('h3') or event_div.find('h4')
            
        if not name_elem:
            logging.warning(f"Could not find event title element")
            # Log the HTML structure for debugging
            html_preview = str(event_div)[:500].replace('\n', ' ')
            logging.debug(f"Event div HTML: {html_preview}...")
            return None
        
        # Try to find the link in the name element or its children
        link = name_elem.find('a')
        if not link:
            logging.warning(f"Could not find link in event title")
            return None
            
        name = name_elem.text.strip()
        event_url = link.get('href')
        
        if not event_url:
            logging.warning(f"Could not find URL in event link")
            return None
            
        # Make sure the URL is absolute
        if not event_url.startswith('http'):
            event_url = f"https://www.nycgovparks.org{event_url}"
            
        logging.info(f"Found event: {name} at URL: {event_url}")
        return {"name": name, "url": event_url}
    except Exception as e:
        logging.error(f"Error parsing event from list: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def standardize_venue(venue_name: str, venue_address: str = None) -> Dict[str, str]:
    """Standardize venue information to match Venue model"""
    return {
        "name": venue_name or "Unknown Venue",
        "address": venue_address,
        "type": "venue"
    }

def parse_event(event_page_soup: BeautifulSoup, event_info: Dict) -> Optional[Dict]:
    """
    Parse the event page and extract detailed information.
    """
    try:
        logging.info(f"Parsing event: {event_info.get('name', 'Unknown')}")
        
        # Find the event div - try multiple approaches
        event_div = event_page_soup.find('div', class_='single_event')
        
        if not event_div:
            logging.warning(f"Could not find event div with class 'single_event' for: {event_info.get('name', 'Unknown')}")
            logging.debug(f"HTML preview: {str(event_page_soup)[:100]}")
            return None
            
        # Extract basic information
        name = event_info.get('name', '')
        if not name and event_div.find('h1'):
            name = event_div.find('h1').text.strip()
        
        # Extract date and time
        start_date = None
        end_date = None
        start_time = None
        end_time = None
        
        # Try to get date from meta tags first
        start_date_meta = event_div.find('meta', {'itemprop': 'startDate'})
        end_date_meta = event_div.find('meta', {'itemprop': 'endDate'})
        
        if start_date_meta and 'content' in start_date_meta.attrs:
            start_datetime = start_date_meta['content']
            try:
                dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                start_date = dt.date()
                start_time = dt.time()
                logging.info(f"Parsed start date from meta: {start_date}, time: {start_time}")
            except ValueError as e:
                logging.warning(f"Could not parse start datetime: {start_datetime}, error: {str(e)}")
        
        if end_date_meta and 'content' in end_date_meta.attrs:
            end_datetime = end_date_meta['content']
            try:
                dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
                end_date = dt.date()
                end_time = dt.time()
                logging.info(f"Parsed end date from meta: {end_date}, time: {end_time}")
            except ValueError as e:
                logging.warning(f"Could not parse end datetime: {end_datetime}, error: {str(e)}")
        
        # If meta tags didn't work, try to get from text
        date_p = None  # Initialize date_p here
        if not start_date:
            date_p = event_div.find('p', class_='single_event_start_date')
            if date_p and date_p.find('strong'):
                date_str = date_p.find('strong').text.strip()
                try:
                    start_date = datetime.strptime(date_str, '%A, %B %d, %Y').date()
                    logging.info(f"Parsed start date from text: {start_date}")
                except ValueError:
                    try:
                        start_date = datetime.strptime(date_str, '%A, %B  %d, %Y').date()
                        logging.info(f"Parsed start date from text (with double space): {start_date}")
                    except ValueError as e:
                        logging.warning(f"Could not parse date string: {date_str}, error: {str(e)}")
        
        # Get time from the paragraph after date
        if date_p and date_p.find_next_sibling('p'):
            time_p = date_p.find_next_sibling('p')
            time_text = time_p.text.strip()
            logging.info(f"Time text: {time_text}")
            
            # Extract time from strong tags
            strong_tags = time_p.find_all('strong')
            if len(strong_tags) >= 2:
                start_time_str = strong_tags[0].text.strip()
                end_time_str = strong_tags[1].text.strip()
                
                logging.info(f"Found time strings: start={start_time_str}, end={end_time_str}")
                
                try:
                    start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
                    logging.info(f"Parsed start time: {start_time}")
                except ValueError as e:
                    logging.warning(f"Could not parse start time: {start_time_str}, error: {str(e)}")
                
                try:
                    end_time = datetime.strptime(end_time_str, '%I:%M %p').time()
                    logging.info(f"Parsed end time: {end_time}")
                except ValueError as e:
                    logging.warning(f"Could not parse end time: {end_time_str}, error: {str(e)}")
            
            # If we couldn't extract from strong tags, try splitting the text
            elif '–' in time_text:
                start_time_str, end_time_str = time_text.split('–')
                start_time_str = start_time_str.replace('strong', '').replace('<', '').replace('>', '').replace('/', '').strip()
                end_time_str = end_time_str.replace('strong', '').replace('<', '').replace('>', '').replace('/', '').strip()
                
                logging.info(f"Split time strings: start={start_time_str}, end={end_time_str}")
                
                try:
                    start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
                    logging.info(f"Parsed start time: {start_time}")
                except ValueError as e:
                    logging.warning(f"Could not parse start time: {start_time_str}, error: {str(e)}")
                
                try:
                    end_time = datetime.strptime(end_time_str, '%I:%M %p').time()
                    logging.info(f"Parsed end time: {end_time}")
                except ValueError as e:
                    logging.warning(f"Could not parse end time: {end_time_str}, error: {str(e)}")
        
        # If we have start_date but not end_date, use start_date for end_date
        if start_date and not end_date:
            end_date = start_date
            logging.info(f"Using start_date for end_date: {end_date}")
        
        # If we have dates but not times, set default times
        if start_date and not start_time:
            start_time = datetime.strptime('12:00 AM', '%I:%M %p').time()
            logging.info(f"Using default start time: {start_time}")
        
        if end_date and not end_time:
            end_time = datetime.strptime('11:59 PM', '%I:%M %p').time()
            logging.info(f"Using default end time: {end_time}")
        
        # Combine date and time
        if start_date and start_time:
            start_datetime = datetime.combine(start_date, start_time)
            # Set timezone to Eastern
            eastern = pytz.timezone('US/Eastern')
            start_datetime = eastern.localize(start_datetime)
            logging.info(f"Combined start datetime: {start_datetime}")
        else:
            start_datetime = None
        
        if end_date and end_time:
            end_datetime = datetime.combine(end_date, end_time)
            # Set timezone to Eastern
            eastern = pytz.timezone('US/Eastern')
            end_datetime = eastern.localize(end_datetime)
            logging.info(f"Combined end datetime: {end_datetime}")
        else:
            end_datetime = None
        
        # Extract description
        description = ""
        desc_div = event_div.find('div', class_='description')
        if desc_div:
            description = desc_div.text.strip()
            logging.info(f"Extracted description: {description[:50]}...")
        
        # Extract venue information
        venue_name = ""
        venue_address = ""
        
        location_div = event_div.find('div', {'itemprop': 'location'})
        if location_div:
            name_span = location_div.find('span', {'itemprop': 'name'})
            if name_span:
                venue_name = name_span.text.strip()
                logging.info(f"Extracted venue name: {venue_name}")
            
            address_div = location_div.find('div', {'itemprop': 'address'})
            if address_div:
                venue_address = address_div.text.strip()
                logging.info(f"Extracted venue address: {venue_address}")
        
        # Extract price
        price = "Free"
        cost_h3 = event_div.find('h3', text='Cost')
        if cost_h3 and cost_h3.find_next_sibling('p'):
            price = cost_h3.find_next_sibling('p').text.strip()
            logging.info(f"Extracted price: {price}")
        
        # Extract organizer
        organizer_name = ""
        organizer_url = ""
        
        organizer_h3 = event_div.find('h3', text='Event Organizer')
        if organizer_h3 and organizer_h3.find_next_sibling('p'):
            organizer_p = organizer_h3.find_next_sibling('p')
            organizer_elem = organizer_p.find('span', {'itemprop': 'name'})
            if organizer_elem:
                organizer_name = organizer_elem.text.strip()
                logging.info(f"Extracted organizer name: {organizer_name}")
            
            organizer_link = organizer_p.find('a')
            if organizer_link and 'href' in organizer_link.attrs:
                organizer_url = organizer_link['href']
                logging.info(f"Extracted organizer URL: {organizer_url}")
        
        # Extract categories
        categories = []
        categories_h3 = event_div.find('h3', text='Categories')
        if categories_h3 and categories_h3.find_next_sibling('p'):
            categories_p = categories_h3.find_next_sibling('p')
            category_links = categories_p.find_all('a')
            for link in category_links:
                categories.append(link.text.strip())
            logging.info(f"Extracted categories: {categories}")
        
        # Generate IDs
        event_id = generate_event_id(name, start_datetime, venue_name) if start_datetime else ""
        location_id = generate_location_id(venue_name)
        
        # Create event dictionary directly (no need for Event class)
        event_dict = {
            "id": event_id,
            "name": name,
            "type": "Event",
            "location_id": location_id,
            "community_id": "com_nycparks",
            "description": description,
            "start_date": start_datetime,
            "end_date": end_datetime,
            "category": [cat.value for cat in determine_categories(categories)],
            "price": {
                "amount": 0 if price.lower() == "free" else float(price.replace('$', '').strip()),
                "type": "free" if price.lower() == "free" else "paid",
                "details": price
            },
            "status": EventStatus.SCHEDULED.value,
            "registration_required": bool(event_div.find('h3', text='Registration')),
            "tags": ["fitness", "nyc parks", "shape up nyc"],
            "metadata": {
                "source_url": event_info.get('url', ''),
                "source_name": "NYC Parks",
                "venue": {
                    "name": venue_name,
                    "address": venue_address,
                    "type": "venue"
                },
                "organizer": {
                    "name": organizer_name,
                    "type": "organizer"
                }
            }
        
        # Create location entry for saving
        location_entry = None
        if venue_name != "Unknown Venue":
            location_entry = {
                "id": location_id,
                "name": venue_name,
                "address": venue_address,
                "type": "venue"
            }
        
        # Return result
        result = {}
        result['event'] = event_dict
        if location_entry:
            result['location'] = location_entry
            
        logging.info(f"Successfully parsed event: {name}")
        return result
    
    except Exception as e:
        logging.error(f"Error parsing event {event_info.get('name', 'Unknown')}: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def fetch_events_from_page(page_num: int) -> tuple[List[Dict], List[Dict]]:
    """
    Fetch events from a specific page of the NYC Parks website.
    Returns a tuple of (events, locations).
    """
    url = f"https://www.nycgovparks.org/events/shape-up-nyc/p{page_num}"
    events = []
    locations = []
    
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            logging.info(f"Attempt {attempt}: Making request with proxy")
            response = make_request(url)
            
            if not response:
                logging.error(f"Failed to fetch events page {page_num}, attempt {attempt}/{max_attempts}")
                time.sleep(5)
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different event div classes
            event_divs = soup.find_all('div', class_='event')
            if not event_divs:
                event_divs = soup.find_all('div', class_='event_item')
            if not event_divs:
                event_divs = soup.find_all('div', class_='event_listing')
                
            logging.info(f"Found {len(event_divs)} event divs on page {page_num}")
            
            # If we found no events, log the HTML structure for debugging
            if len(event_divs) == 0:
                logging.warning(f"No event divs found on page {page_num}")
                html_preview = response.text[:1000].replace('\n', ' ')
                logging.debug(f"HTML preview: {html_preview}...")
                continue
            
            for i, event_div in enumerate(event_divs, 1):
                try:
                    logging.info(f"Processing event {i}/{len(event_divs)} on page {page_num}")
                    
                    # Parse basic event info from the list
                    event_info = parse_event_from_list(event_div)
                    if not event_info:
                        continue
                        
                    # Fetch the event page
                    event_page_soup = fetch_event_page(event_info['url'])
                    if not event_page_soup:
                        continue
                        
                    # Parse detailed event info
                    result = parse_event(event_page_soup, event_info)
                    if not result:
                        continue
                    
                    # Add event and location to their respective lists
                    if 'event' in result:
                        events.append(result['event'])
                        logging.info(f"Added event: {result['event'].get('name', 'Unknown')}")
                    
                    if 'location' in result and result['location']:
                        locations.append(result['location'])
                        logging.info(f"Added location: {result['location'].get('name', 'Unknown')}")
                    
                except Exception as e:
                    logging.error(f"Error processing event {i} on page {page_num}: {str(e)}")
                    logging.error(traceback.format_exc())
                    continue
                    
            # If we got here, we successfully fetched the page
            return events, locations
            
        except Exception as e:
            logging.error(f"Error fetching events from page {page_num}, attempt {attempt}/{max_attempts}: {str(e)}")
            logging.error(traceback.format_exc())
            time.sleep(5)
            
    logging.error(f"Failed to fetch events from page {page_num} after {max_attempts} attempts")
    return [], []

def get_total_pages() -> int:
    """Get the total number of pages"""
    url = "https://www.nycgovparks.org/events/shape-up-nyc/p1"
    
    try:
        response = make_request(url)
        if not response:
            return 1
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find pagination links
        pagination = soup.find('p', class_='parks_pages')
        if not pagination:
            return 1
        
        # Find all page links
        page_links = pagination.find_all('a')
        if not page_links:
            return 1
        
        # Get the last page number
        last_page_link = page_links[-2]  # Skip the "Next" link
        last_page = int(last_page_link.text)
        
        return last_page
    except Exception as e:
        logging.error(f"Error getting total pages: {str(e)}")
        return 1

def main():
    all_events = []
    all_locations = []
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Set maximum pages to scrape
    max_pages = 5
    total_pages = min(get_total_pages(), max_pages)
    logging.info(f"Will scrape {total_pages} pages of events")
    
    # Fetch events from each page
    for page_num in range(1, total_pages + 1):
        logging.info(f"Scraping page {page_num} of {total_pages}")
        events, locations = fetch_events_from_page(page_num)
        all_events.extend(events)
        all_locations.extend(locations)
        
        # Add a longer delay between pages to be more gentle
        if page_num < total_pages:
            time.sleep(5)  # 5 second delay between pages
    
    # Save events
    if all_events:
        try:
            output_file = './data/nyc_parks_events.json'
            with open(output_file, 'w') as f:
                json.dump({"events": all_events}, f, indent=2, default=datetime_serializer)
            logging.info(f"Saved {len(all_events)} events to {output_file}")
        except Exception as e:
            logging.error(f"Failed to save events: {str(e)}")
            logging.error(traceback.format_exc())
    else:
        logging.warning("No events were fetched")
    
    # Save locations
    if all_locations:
        save_locations(all_locations)
    else:
        logging.warning("No locations were found")

if __name__ == "__main__":
    main() 