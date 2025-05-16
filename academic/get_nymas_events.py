#!/usr/bin/env python3
import json
import os
import sys
import logging
import argparse
from datetime import datetime, timezone
import requests
from typing import Dict, List, Tuple, Any, Optional
from bs4 import BeautifulSoup
import re
from dateutil import parser as date_parser
import uuid

# Configure logging
log_dir = "academic/logs"
log_file = os.path.join(log_dir, f"nymas_events_{datetime.now().strftime('%Y%m%d')}.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('get_nymas_events')

def load_json_file(file_path: str) -> Optional[Dict]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json_file(data: Any, file_path: str) -> bool:
    """Save data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")
        return False

def extract_date_info(date_str: str) -> Tuple[str, str]:
    """
    Extract structured date information from NYMAS date strings.
    
    Returns:
        Tuple of (formatted_date, time)
    """
    try:
        # Common patterns seen in the HTML
        date_str = date_str.strip()
        
        # Extract day of week and date
        # Examples: "Friday, Jan. 24th" or "Monday, Sept. 16th"
        day_date_match = re.search(r'([A-Za-z]+),\s+([A-Za-z]+\.?\s+\d+[a-z]{0,2})', date_str)
        
        # Extract time
        time_match = re.search(r'(\d+(?::\d+)?(?:\s*[AP]M)?)\s*([A-Z]{3})?', date_str)
        
        if day_date_match:
            day_of_week = day_date_match.group(1)
            date_part = day_date_match.group(2)
            
            # Construct a date with the current year (can be adjusted later)
            current_year = datetime.now().year
            date_with_year = f"{date_part}, {current_year}"
            
            try:
                parsed_date = date_parser.parse(date_with_year)
                formatted_date = parsed_date.strftime("%Y-%m-%d")
            except:
                # If parsing fails, return the original string
                formatted_date = date_with_year
        else:
            formatted_date = "2025-01-01"  # Default date if parsing fails
        
        if time_match:
            time_str = time_match.group(1)
            timezone_str = time_match.group(2) if time_match.group(2) else "EST"
            time = f"{time_str} {timezone_str}"
        else:
            time = "7:00 PM EST"  # Default time for NYMAS events
            
        return formatted_date, time
    except Exception as e:
        logging.error(f"Error parsing date string '{date_str}': {e}")
        return "2025-01-01", "7:00 PM EST"

def create_iso_datetime(date_str: str, time_str: str) -> str:
    """
    Combine date and time strings to create an ISO formatted datetime string.
    """
    try:
        # Handle "7PM EST" format
        time_str = time_str.replace("PM", " PM").replace("AM", " AM")
        
        # Combine date and time
        datetime_str = f"{date_str} {time_str}"
        
        # Parse the combined string
        dt = date_parser.parse(datetime_str)
        
        # Format as ISO string
        return dt.isoformat()
    except Exception as e:
        logging.error(f"Error creating ISO datetime from '{date_str}' and '{time_str}': {e}")
        # Return a default value if parsing fails
        return "2025-01-01T19:00:00-05:00"

def fetch_nymas_events(url: str = "https://www.nymas.org/schedule") -> List[Dict]:
    """
    Scrape events from the NYMAS website.
    
    Args:
        url: The URL of the NYMAS schedule page
        
    Returns:
        List of event dictionaries
    """
    try:
        logging.info(f"Fetching events from {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        events = []
        
        # Look for event sections - structure will depend on the actual HTML
        event_sections = soup.select('div[role="wixui-box"]')
        
        for section in event_sections:
            try:
                # Skip sections that don't seem to contain event data
                if not section.select_one('span.wixui-rich-text__text'):
                    continue
                
                # Extract date
                date_elem = section.select_one('p.font_7:-soup-contains("PM EST")')
                if not date_elem:
                    date_elem = section.select_one('p.font_8:-soup-contains("PM EST")')
                
                if not date_elem:
                    continue
                
                date_text = date_elem.get_text().strip()
                formatted_date, time_str = extract_date_info(date_text)
                
                # Extract title
                title_elem = section.select_one('div.lq2cno p.font_7, div.lq2cno p.font_8')
                title = title_elem.get_text().strip() if title_elem else "NYMAS Event"
                
                # Extract speaker
                speaker_elem = section.select_one('div:-soup-contains("Speaker") + div p')
                if not speaker_elem:
                    speaker_elem = section.select_one('p.font_7:-soup-contains-one(":")') 
                
                speaker = speaker_elem.get_text().strip() if speaker_elem else "TBD"
                
                # Extract affiliation/description
                affiliation_elem = section.select_one('div:-soup-contains("Affiliation") + div p')
                if not affiliation_elem:
                    # Try to find element that might contain affiliation info
                    affiliation_elem = section.select_one('p.font_8:-soup-contains-one("University")')
                
                affiliation = affiliation_elem.get_text().strip() if affiliation_elem else ""
                
                # Extract location and link
                location_elem = section.select_one('a:-soup-contains("Online"), a:-soup-contains("Lubin")')
                location = "Online"
                event_url = ""
                
                if location_elem:
                    location_text = location_elem.get_text().strip()
                    location = location_text if location_text else "Online"
                    
                    # Try to get URL if it's an online event
                    if "href" in location_elem.attrs:
                        event_url = location_elem["href"]
                        
                        # Clean Zoom URLs if needed
                        if "zoom.us" in event_url and event_url.count("https") > 1:
                            # Handle duplicated URLs
                            event_url = event_url.split("https://")[1]
                            event_url = f"https://{event_url}"
                
                # Create ISO datetime
                start_datetime = create_iso_datetime(formatted_date, time_str)
                
                # Calculate end time (assume 1.5 hour events)
                try:
                    start_dt = date_parser.parse(start_datetime)
                    end_dt = start_dt.replace(hour=start_dt.hour + 1, minute=start_dt.minute + 30)
                    end_datetime = end_dt.isoformat()
                except Exception as e:
                    logging.error(f"Error calculating end time: {e}")
                    end_datetime = start_datetime  # Use same time as fallback
                
                # Create a description combining title and affiliation
                description = f"{title}"
                if affiliation:
                    description += f"\n\nSpeaker: {speaker}\n{affiliation}"
                else:
                    description += f"\n\nSpeaker: {speaker}"
                
                # Generate a unique ID
                event_id = f"nymas_{formatted_date}_{uuid.uuid4().hex[:8]}"
                
                # Create event dictionary in the standardized format
                event = {
                    "id": event_id,
                    "name": title,
                    "description": description,
                    "startDate": start_datetime,
                    "endDate": end_datetime,
                    "location": "Lubin House, New York, NY" if "Lubin" in location else "Online via Zoom",
                    "url": event_url,
                    "category": "tech_talks",
                    "subcategory": "tech_panels",
                    "free": True,
                    "price": 0,
                    "priceType": "Free",
                    "details": f"Speaker: {speaker}",
                    "capacity": 100,
                    "registrationRequired": location == "Online",
                    "image": "default-event.jpg",
                    "status": "upcoming" if datetime.now(timezone.utc) < date_parser.parse(start_datetime).replace(tzinfo=timezone.utc) else "past",
                    "metadata": {
                        "source_url": url,
                        "speakers": [{"name": speaker, "title": ""}],
                        "venue": {
                            "name": "NYMAS" + (" - Lubin House" if "Lubin" in location else " - Online"),
                            "address": "NYMAS, New York, NY",
                            "type": "Academic"
                        },
                        "institution": "New York Military Affairs Symposium"
                    }
                }
                
                events.append(event)
                logging.info(f"Added event: {title} on {formatted_date}")
                
            except Exception as e:
                logging.error(f"Error processing event section: {e}")
                continue
        
        logging.info(f"Found {len(events)} events from NYMAS")
        return events
    
    except Exception as e:
        logging.error(f"Error fetching NYMAS events: {e}")
        return []

def create_sample_nymas_events() -> List[Dict]:
    """
    Create sample NYMAS events if scraping fails.
    """
    now = datetime.now(timezone.utc)
    
    # Sample events
    sample_events = [
        {
            "title": "Battle of the Borderlands, 1919-1920: Russia, Poland, and Ukraine",
            "speaker": "Steve Zaloga",
            "date": "2025-10-25",
            "time": "7:00 PM EST",
            "location": "Online",
            "url": "https://us02web.zoom.us/j/81285414286"
        },
        {
            "title": "The Battle of Adrianople, August 9, A.D. 378",
            "speaker": "Richard Van Nort",
            "date": "2025-11-15",
            "time": "7:00 PM EST",
            "location": "Online",
            "url": "https://us02web.zoom.us/j/88994395897"
        },
        {
            "title": "The Battle for Attu, 1943",
            "speaker": "Theodore Cook",
            "date": "2025-12-02",
            "time": "7:00 PM EST", 
            "location": "Lubin House",
            "url": ""
        }
    ]
    
    events = []
    for sample in sample_events:
        start_datetime = create_iso_datetime(sample["date"], sample["time"])
        try:
            start_dt = date_parser.parse(start_datetime)
            end_dt = start_dt.replace(hour=start_dt.hour + 1, minute=start_dt.minute + 30)
            end_datetime = end_dt.isoformat()
        except:
            end_datetime = start_datetime
            
        event_id = f"nymas_{sample['date']}_{uuid.uuid4().hex[:8]}"
        
        event = {
            "id": event_id,
            "name": sample["title"],
            "description": f"{sample['title']}\n\nSpeaker: {sample['speaker']}",
            "startDate": start_datetime,
            "endDate": end_datetime,
            "location": "Lubin House, New York, NY" if "Lubin" in sample["location"] else "Online via Zoom",
            "url": sample["url"],
            "category": "tech_talks",
            "subcategory": "tech_panels",
            "free": True,
            "price": 0,
            "priceType": "Free",
            "details": f"Speaker: {sample['speaker']}",
            "capacity": 100,
            "registrationRequired": sample["location"] == "Online",
            "image": "default-event.jpg",
            "status": "upcoming" if datetime.now(timezone.utc) < date_parser.parse(start_datetime).replace(tzinfo=timezone.utc) else "past",
            "metadata": {
                "source_url": "https://www.nymas.org/schedule",
                "speakers": [{"name": sample["speaker"], "title": ""}],
                "venue": {
                    "name": "NYMAS" + (" - Lubin House" if "Lubin" in sample["location"] else " - Online"),
                    "address": "NYMAS, New York, NY",
                    "type": "Academic"
                },
                "institution": "New York Military Affairs Symposium"
            }
        }
        
        events.append(event)
    
    return events

def get_nymas_events(output_path: str) -> List[Dict]:
    """
    Get events from NYMAS and save them to a file.
    
    Args:
        output_path: Path where to save the events
        
    Returns:
        List of events
    """
    # First try to scrape events from the website
    events = fetch_nymas_events()
    
    # If scraping fails or returns no events, use sample events
    if not events:
        logging.warning("Failed to scrape NYMAS events. Using sample events instead.")
        events = create_sample_nymas_events()
    
    # Save events to file
    if output_path and events:
        save_json_file({"events": events}, output_path)
        logging.info(f"Saved {len(events)} NYMAS events to {output_path}")
    
    return events

def main():
    """Main entry point."""
    try:
        # Set up command line arguments
        parser = argparse.ArgumentParser(description='Extract events from NYMAS website')
        parser.add_argument('--output', '-o', default='academic/data/nymas_events.json', help='Output file path')
        parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
        parser.add_argument('--sample', '-s', action='store_true', help='Use sample events instead of scraping')
        args = parser.parse_args()
        
        # Configure more verbose logging if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        logging.info(f"Output will be saved to: {args.output}")
        
        # Get events (either by scraping or using samples)
        if args.sample:
            logging.info("Using sample events as requested")
            events = create_sample_nymas_events()
            save_json_file({"events": events}, args.output)
            logging.info(f"Saved {len(events)} sample NYMAS events to {args.output}")
        else:
            events = get_nymas_events(args.output)
        
        logging.info(f"Successfully processed {len(events)} NYMAS events")
        
        return 0
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 