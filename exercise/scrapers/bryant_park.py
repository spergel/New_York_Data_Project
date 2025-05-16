import os
import json
import requests
import hashlib
import logging
import pytz
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('scraper.log'), logging.StreamHandler()]
)

# Base URL for Bryant Park
BASE_URL = 'https://bryantpark.org'
BOOT_CAMP_URL = f'{BASE_URL}/activities/boot-camp'

# Bryant Park venue coordinates - for venue-coordinates.json
BRYANT_PARK_COORDINATES = {
    "Bryant Park, New York, NY": {
        "latitude": 40.7536,
        "longitude": -73.9832
    }
}

def get_event_details(event_url: str) -> Optional[Dict]:
    """Fetch detailed event information from Bryant Park event page"""
    try:
        response = requests.get(event_url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch event details: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract more detailed information from the event page
        # This would need to be customized based on the actual page structure
        event_details = {}
        
        # Get event description
        description_div = soup.select_one('.activityMainContent')
        if description_div:
            event_details['description'] = description_div.get_text(strip=True)
        
        # Additional details like location, time, etc. can be extracted here
        
        return event_details
        
    except Exception as e:
        logging.error(f"Error fetching event details: {e}")
        return None

def parse_event_datetime(date_str: str, time_str: str) -> datetime:
    """Parse date and time strings into datetime object"""
    # Example format: "Wed. March 12, 2025" and "7:00am"
    try:
        # Remove day of week and any other non-essential parts
        date_parts = date_str.split('. ', 1)[1] if '. ' in date_str else date_str
        
        # Create full datetime string and parse
        date_time_str = f"{date_parts} {time_str}"
        eastern = pytz.timezone('America/New_York')
        
        # This pattern matches various date formats in Bryant Park events
        dt = datetime.strptime(date_time_str, "%B %d, %Y %I:%M%p")
        return eastern.localize(dt)
    except Exception as e:
        logging.error(f"Error parsing date and time: {e}, {date_str}, {time_str}")
        # Return a future date to avoid breaking the scraper
        return datetime.now(pytz.timezone('America/New_York')) + timedelta(days=30)

def get_bryant_park_events(url: str = BOOT_CAMP_URL) -> List[Dict]:
    """Scrape events from Bryant Park website"""
    events = []
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch page: {response.status_code}")
            return events
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all event cards on the page
        event_cards = soup.select('li.card.calendarEventCard')
        
        for card in event_cards:
            try:
                # Extract basic event information
                title_element = card.select_one('.cardTitle a')
                if not title_element:
                    continue
                
                title = title_element.get_text(strip=True)
                event_url = urljoin(BASE_URL, title_element['href'])
                
                # Extract date and time
                date_time_element = card.select_one('.cardFlag time')
                if not date_time_element:
                    continue
                
                date_str = date_time_element.get_text().split('at')[0].strip()
                time_str = date_time_element.get_text().split('at')[1].strip()
                
                # Parse location from Google Maps link
                location_element = card.select_one('.actionIconsList a[href*="maps"]')
                location = ""
                if location_element:
                    location = "Bryant Park, New York, NY"  # Default location
                
                # Extract image URL if available
                image_element = card.select_one('img')
                image_url = ""
                if image_element and 'data-src' in image_element.attrs:
                    image_url = urljoin(BASE_URL, image_element['data-src'])
                
                # Get event start and end time
                start_date = parse_event_datetime(date_str, time_str)
                # Assuming events are 1 hour by default
                end_date = start_date + timedelta(hours=1)
                
                # Generate unique ID
                unique_id = f"{title}{start_date.isoformat()}".encode()
                event_id = hashlib.md5(unique_id).hexdigest()[:8]
                
                # Get more details from event page
                additional_details = get_event_details(event_url) or {}
                
                # Determine category based on title or other info
                # For Boot Camp events, use "body workout" category
                category = "body workout"
                
                # Create event dictionary with structure matching FitConnect app
                event = {
                    "id": f"bryant_park_{event_id}",
                    "name": title,
                    "description": additional_details.get('description', ''),
                    "category": category,
                    "community_id": "com_bryant_park",
                    "location": "loc_bryant_park",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "image_url": image_url,
                    "metadata": {
                        "source_url": event_url,
                        "venue": {
                            "name": "Bryant Park",
                            "address": "Bryant Park, New York, NY",
                            "coordinates": {
                                "latitude": 40.7536,  # Bryant Park coordinates
                                "longitude": -73.9832
                            },
                            "type": "venue"
                        },
                        "organizer": "Bryant Park Corporation"
                    },
                    "price": {
                        "is_free": True,
                        "price_range": "Free",
                        "currency": "USD"
                    },
                    "tags": ["boot camp", "fitness", "outdoor"],
                    "community_id": "bryant_park"
                }
                
                events.append(event)
                
            except Exception as e:
                logging.error(f"Error processing event card: {e}")
                continue
        
    except Exception as e:
        logging.error(f"Error fetching events: {e}")
    
    return events

def is_future_event(event: Dict) -> bool:
    """Check if the event is in the future"""
    try:
        # Convert ISO format string to datetime
        start_date_str = event.get('start_date', '')
        if not start_date_str:
            return False
            
        start_date = datetime.fromisoformat(start_date_str)
        return start_date > datetime.now(start_date.tzinfo)
        
    except Exception as e:
        logging.error(f"Error checking if event is in future: {e}")
        return False



def main():
    logging.info("Starting Bryant Park event scraper...")
    
    # Update venue coordinates with Bryant Park location
    
    # Fetch Bryant Park events
    all_events = get_bryant_park_events()
    
    # Filter out past events
    filtered_events = [event for event in all_events if is_future_event(event)]
    
    # Save filtered events to file
    output = {"events": filtered_events}
    output_file = 'fitconnect-nyc/src/data/bryant_park_events.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Total future events collected: {len(filtered_events)}")
    logging.info(f"Events saved to {output_file}")

if __name__ == '__main__':
    main()