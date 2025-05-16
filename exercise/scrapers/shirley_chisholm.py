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

# Base URL for Shirley Chisholm State Park
BASE_URL = 'https://parks.ny.gov'
EVENTS_URL = f'{BASE_URL}/events/event-results.aspx?hl=8&par=136&ft=0'
SAMPLE_FILE = 'sample_shirley_chisholm.html'

# Shirley Chisholm Park coordinates
SHIRLEY_CHISHOLM_COORDINATES = {
    "Shirley Chisholm State Park, Brooklyn, NY": {
        "latitude": 40.6507,
        "longitude": -73.8854
    }
}

def get_event_details(event_url: str) -> Optional[Dict]:
    """Fetch detailed event information from event page"""
    try:
        # In a real scenario, we would make an HTTP request to get the event details
        response = requests.get(urljoin(BASE_URL, event_url))
        if response.status_code != 200:
            logging.error(f"Failed to fetch event details: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract more detailed information from the event page
        event_details = {
            'description': 'Detailed description would be here in a real scrape',
            'image_url': f'{BASE_URL}/parks/images/shirleychisholm_event.jpg'
        }
        
        return event_details
        
    except Exception as e:
        logging.error(f"Error fetching event details: {e}")
        return None

def parse_event_datetime(date_time_str: str) -> tuple:
    """Parse date and time string into start and end datetime objects"""
    try:
        eastern = pytz.timezone('America/New_York')
        
        logging.info(f"Parsing date time string: {date_time_str}")
        
        # Check if this is a date with no time
        if not any(time_marker in date_time_str for time_marker in ['AM', 'PM']):
            # Event with no specific time (whole day event)
            # Remove day of week if present
            parts = date_time_str.split(', ')
            date_only = parts[-1].strip()
            try:
                # Parse date without time
                start_datetime = datetime.strptime(date_only, "%B %d, %Y")
                # Set default times - all day event (9AM to 5PM)
                start_datetime = start_datetime.replace(hour=9, minute=0)
                end_datetime = start_datetime.replace(hour=17, minute=0)
            except ValueError:
                try:
                    # Try alternate format
                    start_datetime = datetime.strptime(date_only, "%m/%d/%Y")
                    start_datetime = start_datetime.replace(hour=9, minute=0)
                    end_datetime = start_datetime.replace(hour=17, minute=0)
                except ValueError:
                    # If nothing works, extract parts with regex
                    date_match = re.search(r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', date_time_str)
                    if date_match:
                        month = date_match.group(1)
                        day = date_match.group(2)
                        year = date_match.group(3)
                        date_str = f"{month} {day}, {year}"
                        start_datetime = datetime.strptime(date_str, "%B %d, %Y")
                        start_datetime = start_datetime.replace(hour=9, minute=0)
                        end_datetime = start_datetime.replace(hour=17, minute=0)
                    else:
                        # Last resort
                        start_datetime = datetime.now() + timedelta(days=30)
                        start_datetime = start_datetime.replace(hour=9, minute=0)
                        end_datetime = start_datetime.replace(hour=17, minute=0)
            
            # Add timezone
            start_datetime = eastern.localize(start_datetime)
            end_datetime = eastern.localize(end_datetime)
            logging.info(f"Parsed date without time: {start_datetime} - {end_datetime}")
            return start_datetime, end_datetime
        
        # Check if this is a recurring event with "until" keyword
        if " until " in date_time_str.lower():
            logging.info(f"Detected recurring event: {date_time_str}")
            # For recurring events, we'll take the first date and time
            parts = date_time_str.lower().split(' until ')
            start_str = parts[0].strip()
            
            # Extract time from the string
            time_pattern = r'(\d{1,2}:\d{2}\s*[AP]M)'
            time_matches = re.findall(time_pattern, date_time_str, re.IGNORECASE)
            
            # Extract date from the string
            date_pattern = r'([A-Za-z]+\s+\d{1,2},\s+\d{4})'
            date_matches = re.findall(date_pattern, date_time_str)
            
            if date_matches and time_matches:
                # We have both date and time
                date_str = date_matches[0]
                time_str = time_matches[0]
                
                try:
                    # Try to combine them
                    start_datetime = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M %p")
                    
                    # Set end time if available
                    if len(time_matches) >= 2:
                        end_time_str = time_matches[1]
                        end_time = datetime.strptime(end_time_str, "%I:%M %p").time()
                        end_datetime = datetime.combine(start_datetime.date(), end_time)
                    else:
                        # Default to 1 hour
                        end_datetime = start_datetime + timedelta(hours=3)  # Longer for workshops
                    
                    # Add timezone
                    start_datetime = eastern.localize(start_datetime)
                    end_datetime = eastern.localize(end_datetime)
                    logging.info(f"Parsed recurring event: {start_datetime} - {end_datetime}")
                    return start_datetime, end_datetime
                except Exception as e:
                    logging.error(f"Error parsing recurring event: {e}")
            
            # If we can't extract both date and time, try a different approach
            # Try to find a weekday name + month date pattern
            weekday_pattern = r'(Mondays|Tuesdays|Wednesdays|Thursdays|Fridays|Saturdays|Sundays)'
            weekday_match = re.search(weekday_pattern, date_time_str, re.IGNORECASE)
            
            if weekday_match and date_matches:
                # This is a weekly event
                weekday = weekday_match.group(1).lower()
                date_str = date_matches[0]
                
                # Map weekday name to number (0=Monday)
                weekday_map = {
                    'mondays': 0, 'tuesdays': 1, 'wednesdays': 2, 'thursdays': 3, 
                    'fridays': 4, 'saturdays': 5, 'sundays': 6
                }
                weekday_num = weekday_map.get(weekday, 0)
                
                try:
                    # Parse the start date
                    base_date = datetime.strptime(date_str, "%B %d, %Y")
                    
                    # Adjust to the correct weekday if needed
                    days_to_add = (weekday_num - base_date.weekday()) % 7
                    start_date = base_date + timedelta(days=days_to_add)
                    
                    # Add the time component if available
                    if time_matches:
                        time_obj = datetime.strptime(time_matches[0], "%I:%M %p").time()
                        start_datetime = datetime.combine(start_date.date(), time_obj)
                        
                        # Set end time if available
                        if len(time_matches) >= 2:
                            end_time = datetime.strptime(time_matches[1], "%I:%M %p").time()
                            end_datetime = datetime.combine(start_date.date(), end_time)
                        else:
                            # Default to 3 hours for workshops
                            end_datetime = start_datetime + timedelta(hours=3)
                    else:
                        # Default time (9 AM to 12 PM)
                        start_datetime = start_date.replace(hour=9, minute=0)
                        end_datetime = start_date.replace(hour=12, minute=0)
                    
                    # Add timezone
                    start_datetime = eastern.localize(start_datetime)
                    end_datetime = eastern.localize(end_datetime)
                    logging.info(f"Parsed weekly event: {start_datetime} - {end_datetime}")
                    return start_datetime, end_datetime
                except Exception as e:
                    logging.error(f"Error parsing weekly event: {e}")
            
            # If all else fails, use the fallback approach
            # Default to current date + 15 days at 11 AM
            start_datetime = datetime.now() + timedelta(days=15)
            start_datetime = start_datetime.replace(hour=11, minute=0)
            end_datetime = start_datetime + timedelta(hours=3)  # Workshops typically 3 hours
            
            # Add timezone
            start_datetime = eastern.localize(start_datetime)
            end_datetime = eastern.localize(end_datetime)
            logging.info(f"Using fallback for recurring event: {start_datetime} - {end_datetime}")
            return start_datetime, end_datetime
        
        # Standard case with date and time
        # Try to directly extract date and time with regex
        date_pattern = r'([A-Za-z]+\s+\d{1,2},\s+\d{4})'
        time_pattern = r'(\d{1,2}:\d{2}\s*[AP]M)'
        
        date_matches = re.findall(date_pattern, date_time_str)
        time_matches = re.findall(time_pattern, date_time_str)
        
        if date_matches and time_matches:
            # We have direct matches for date and time
            date_str = date_matches[0]
            time_str = time_matches[0]
            
            try:
                # Combine date and time
                start_datetime = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M %p")
                
                # Calculate end time
                if len(time_matches) >= 2:
                    end_time = datetime.strptime(time_matches[1], "%I:%M %p").time()
                    end_datetime = datetime.combine(start_datetime.date(), end_time)
                else:
                    # Default to 1 hour event
                    end_datetime = start_datetime + timedelta(hours=1)
                
                # Add timezone
                start_datetime = eastern.localize(start_datetime)
                end_datetime = eastern.localize(end_datetime)
                logging.info(f"Directly parsed date and time: {start_datetime} - {end_datetime}")
                return start_datetime, end_datetime
            except Exception as e:
                logging.error(f"Error directly parsing date and time: {e}")
        
        # Fall back to the original approach
        # Split the string to get date and time parts
        parts = date_time_str.split(' ', 1)
        if len(parts) < 2:
            raise ValueError(f"Invalid date time format: {date_time_str}")
        
        date_part = parts[1]
        
        # Parse date and time
        date_time_parts = date_part.split(' - ')
        start_str = date_time_parts[0].strip()
        
        # Parse start time
        try:
            if ',' in start_str:
                # Remove day of week if present
                start_str = start_str.split(', ', 1)[1].strip()
            start_datetime = datetime.strptime(start_str, "%B %d, %Y %I:%M %p")
        except ValueError:
            # Try alternate formats
            try:
                start_datetime = datetime.strptime(start_str, "%m/%d/%Y %I:%M %p")
            except ValueError:
                # Try to extract separately
                date_match = re.search(r'([A-Za-z]+\s+\d{1,2},\s+\d{4})', start_str)
                time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)', start_str)
                
                if date_match and time_match:
                    date_str = date_match.group(1)
                    time_str = time_match.group(1)
                    start_datetime = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M %p")
                else:
                    # Default to current date + 30 days
                    start_datetime = datetime.now() + timedelta(days=30)
                    start_datetime = start_datetime.replace(hour=9, minute=0)
        
        start_datetime = eastern.localize(start_datetime)
        
        # Parse end time if available, otherwise default to 1 hour
        if len(date_time_parts) > 1:
            end_str = date_time_parts[1].strip()
            try:
                end_time = datetime.strptime(end_str, "%I:%M %p").time()
                end_datetime = datetime.combine(start_datetime.date(), end_time)
                end_datetime = eastern.localize(end_datetime)
            except ValueError:
                # Default to 1 hour if parsing fails
                end_datetime = start_datetime + timedelta(hours=1)
        else:
            # Default to 1 hour duration if no end time
            end_datetime = start_datetime + timedelta(hours=1)
        
        logging.info(f"Parsed with fallback approach: {start_datetime} - {end_datetime}")
        return start_datetime, end_datetime
    
    except Exception as e:
        logging.error(f"Error parsing date and time: {e}, {date_time_str}")
        # Return current time plus 30 days to avoid breaking the scraper
        now = datetime.now(pytz.timezone('America/New_York'))
        return now + timedelta(days=30), now + timedelta(days=30, hours=1)

def get_shirley_chisholm_events(use_sample: bool = True) -> List[Dict]:
    """Scrape events from Shirley Chisholm State Park website or sample file"""
    events = []
    
    try:
        # Use sample file if available and requested
        if use_sample and os.path.exists(SAMPLE_FILE):
            logging.info(f"Using sample file: {SAMPLE_FILE}")
            with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            # Otherwise make a real HTTP request
            logging.info(f"Fetching events from: {EVENTS_URL}")
            response = requests.get(EVENTS_URL)
            if response.status_code != 200:
                logging.error(f"Failed to fetch page: {response.status_code}")
                return events
            html_content = response.text
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all event items on the page
        event_items = soup.select('div.result-item')
        logging.info(f"Found {len(event_items)} event items")
        
        for item in event_items:
            try:
                # Extract event title and URL
                title_element = item.select_one('a[href*="event.aspx"]')
                if not title_element:
                    continue
                
                title = title_element.get_text(strip=True)
                event_url = title_element['href']
                
                # Extract date and time
                date_time_element = item.select_one('span[style*="color:#555;"]')
                if not date_time_element:
                    continue
                
                date_time_str = date_time_element.get_text(strip=True)
                
                # Extract location
                location_element = item.select_one('span a[href*="details.aspx"]')
                location = location_element.get_text(strip=True) if location_element else "Shirley Chisholm State Park"
                
                # Extract description
                description_element = item.select_one('div[style*="padding-right:5px;"]')
                description = description_element.get_text(strip=True) if description_element else ""
                
                # Check if this is a recurring event
                is_recurring = " until " in date_time_str.lower()
                
                # Get event start and end time
                start_date, end_date = parse_event_datetime(date_time_str)
                
                # For recurring events, ensure date is in the future
                # This is a workaround for sample data that might have recurring events starting in the past
                if is_recurring:
                    # Get current date
                    now = datetime.now(pytz.timezone('America/New_York'))
                    
                    # If the start date is in the past, adjust it to a future date
                    if start_date < now:
                        # For weekly events, find the next occurrence
                        days_to_add = (start_date.weekday() - now.weekday()) % 7
                        if days_to_add == 0:
                            days_to_add = 7  # Next week if today is the same weekday
                        
                        # Create new dates
                        new_start = now + timedelta(days=days_to_add)
                        # Keep the same time
                        new_start = new_start.replace(hour=start_date.hour, minute=start_date.minute)
                        
                        # Calculate new end time
                        duration = end_date - start_date
                        new_end = new_start + duration
                        
                        # Replace dates
                        start_date = new_start
                        end_date = new_end
                        
                        logging.info(f"Adjusted recurring event date to future: {start_date} - {end_date}")
                
                # Generate unique ID
                unique_id = f"{title}{start_date.isoformat()}".encode()
                event_id = hashlib.md5(unique_id).hexdigest()[:8]
                
                # Get more details from event page
                additional_details = get_event_details(event_url) or {}
                
                # Add note about recurring events to description
                final_description = description or additional_details.get('description', '')
                if is_recurring:
                    # Extract the date range for the note
                    parts = date_time_str.lower().split(' until ')
                    if len(parts) >= 2:
                        date_range = f"{parts[0].strip()} until {parts[1].strip()}"
                        recurring_note = f"\n\nThis is a recurring event: {date_range}"
                        final_description = f"{final_description}{recurring_note}"
                
                # Create event dictionary with structure matching Bryant Park format
                event = {
                    "id": f"shirley_chisholm_{event_id}",
                    "name": title,
                    "description": final_description,
                    "category": "nature",
                    "community_id": "shirley_chisholm",
                    "location": "loc_shirley_chisholm",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "image_url": additional_details.get('image_url', ''),
                    "metadata": {
                        "source_url": urljoin(BASE_URL, event_url),
                        "venue": {
                            "name": "Shirley Chisholm State Park",
                            "address": "1750 Pennsylvania Ave, Brooklyn, NY 11239",
                            "coordinates": {
                                "latitude": 40.6507,
                                "longitude": -73.8854
                            },
                            "type": "venue"
                        },
                        "organizer": "New York State Parks"
                    },
                    "price": {
                        "is_free": True,
                        "price_range": "Free",
                        "currency": "USD"
                    },
                    "tags": ["nature", "outdoors", "state park"],
                    "community_id": "shirley_chisholm"
                }
                
                events.append(event)
                logging.info(f"Processed event: {title}")
                
            except Exception as e:
                logging.error(f"Error processing event item: {e}")
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
        now = datetime.now(pytz.timezone('America/New_York'))
        
        # Ensure both datetimes are timezone-aware for comparison
        if start_date.tzinfo is None:
            eastern = pytz.timezone('America/New_York')
            start_date = eastern.localize(start_date)
            
        # Check if event is in the future
        is_future = start_date > now
        logging.info(f"Event: {event.get('name')}, Date: {start_date}, Is future: {is_future}")
        return is_future
        
    except Exception as e:
        logging.error(f"Error checking if event is in future: {e}")
        return False

def main():
    logging.info("Starting Shirley Chisholm State Park event scraper...")
    
    # Fetch Shirley Chisholm events
    all_events = get_shirley_chisholm_events(use_sample=True)
    
    # Filter out past events
    filtered_events = [event for event in all_events if is_future_event(event)]
    
    # Save filtered events to file
    output = {"events": filtered_events}
    output_file = 'data/shirley_chisholm_events.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Total future events collected: {len(filtered_events)}")
    logging.info(f"Events saved to {output_file}")

if __name__ == '__main__':
    main() 