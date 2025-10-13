#!/usr/bin/env python3
"""
Pratt Institute Events Scraper
Scrapes events from Pratt Institute's events page
"""

import requests
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urljoin
from date_utils import create_event_dates, create_multi_day_event_dates, standardize_datetime

def scrape_pratt_events():
    """Scrape events from Pratt Institute"""
    print("Scraping Pratt Institute events...")
    
    base_url = "https://www.pratt.edu"
    events_url = "https://www.pratt.edu/events/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Get the main events page
        print("Fetching main events page...")
        response = requests.get(events_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        all_events = []
        
        # Method 1: Featured slider events
        print("Looking for featured events...")
        featured_events = soup.find_all('div', class_='tease js-slider__slide tease--event-featured tease--has-image')
        print(f"Found {len(featured_events)} featured events")
        
        for teaser in featured_events:
            event = extract_event_from_teaser(teaser, base_url)
            if event:
                all_events.append(event)
        
        # Method 2: Regular event listings
        print("Looking for regular events...")
        regular_events = soup.find_all('div', class_='tease')
        print(f"Found {len(regular_events)} regular events")
        
        for teaser in regular_events:
            if teaser not in featured_events:  # Avoid duplicates
                event = extract_event_from_teaser(teaser, base_url)
                if event:
                    all_events.append(event)
        
        # Method 3: Look for event headers
        print("Looking for event headers...")
        event_headers = soup.find_all('h2')
        print(f"Found {len(event_headers)} headers")
        
        for header in event_headers:
            event = extract_event_from_header(header, base_url)
            if event:
                all_events.append(event)
        
        # Method 4: Look for any div with event-like content
        print("Looking for event containers...")
        event_containers = soup.find_all('div', class_=lambda x: x and 'event' in x.lower())
        print(f"Found {len(event_containers)} event containers")
        
        for container in event_containers:
            if container not in featured_events and container not in regular_events:
                event = extract_event_from_container(container, base_url)
                if event:
                    all_events.append(event)
        
        print(f"Found {len(all_events)} total potential events")
        
        # Remove duplicates based on name
        unique_events = []
        seen_names = set()
        for event in all_events:
            if event['name'] not in seen_names:
                unique_events.append(event)
                seen_names.add(event['name'])
        
        print(f"After deduplication: {len(unique_events)} unique events")
        
        # Save debug output
        debug_data = {
            "scraped_at": standardize_datetime(datetime.now()),
            "total_events": len(unique_events),
            "events": unique_events
        }
        
        with open('pratt_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved debug output to pratt_events_debug.json")
        
        return {"events": unique_events}
        
    except Exception as e:
        print(f"Error scraping Pratt events: {e}")
        return {"events": []}

def extract_event_from_teaser(teaser, base_url):
    """Extract basic event info from teaser element"""
    try:
        # Get title and URL
        title_elem = teaser.find('h2', class_='tease__title')
        if not title_elem:
            title_elem = teaser.find('h2') or teaser.find('h3') or teaser.find('h4')
        
        if not title_elem:
            return None
            
        title_link = title_elem.find('a', class_='tease__title-link')
        if not title_link:
            title_link = title_elem.find('a')
        
        if title_link:
            name = title_link.get_text(strip=True)
            event_url = urljoin(base_url, title_link.get('href'))
        else:
            name = title_elem.get_text(strip=True)
            event_url = None
        
        if not name or len(name) < 3:
            return None
        
        # Get date and time
        start_date = None
        end_date = None
        
        date_elem = teaser.find('p', class_='tease__date')
        if date_elem:
            date_day = date_elem.find('span', class_='tease__date-day')
            date_time = date_elem.find('span', class_='tease__date-time')
            
            if date_day:
                date_text = date_day.get_text(strip=True)
                time_text = date_time.get_text(strip=True) if date_time else ""
                
                # Parse the date using standardized utilities
                if "–" in date_text or "-" in date_text:
                    # Multi-day event
                    date_parts = re.split(r'[–\-]', date_text)
                    if len(date_parts) == 2:
                        start_date_str = date_parts[0].strip()
                        end_date_str = date_parts[1].strip()
                        start_date, end_date = create_multi_day_event_dates(start_date_str, end_date_str, time_text)
                else:
                    # Single day event
                    start_date, end_date = create_event_dates(date_text, time_text)
        
        # Get location
        location = "Pratt Institute"
        location_elem = teaser.find('p', class_='tease__location')
        if location_elem:
            location = location_elem.get_text(strip=True)
        
        # Generate event ID
        event_id = hashlib.md5(f"pratt_{name}_{event_url or 'no_url'}".encode()).hexdigest()
        
        return {
            "id": event_id,
            "name": name,
            "description": f"Event at {location}",
            "start_date": start_date,  # Already standardized
            "end_date": end_date,      # Already standardized
            "location_id": "pratt_institute",
            "community_id": "pratt_institute",
            "category": "academic",
            "url": event_url,
            "metadata": {
                "source": "pratt_institute",
                "source_group": "Pratt",
                "scraped_at": standardize_datetime(datetime.now()),
                "extraction_method": "teaser"
            }
        }
        
    except Exception as e:
        print(f"Error extracting teaser data: {e}")
        return None

def extract_event_from_header(header_elem, base_url):
    """Extract event info from a header element"""
    try:
        name = header_elem.get_text(strip=True)
        if not name or len(name) < 3:
            return None
        
        # Look for nearby date/location info
        parent = header_elem.parent
        if not parent:
            return None
        
        parent_text = parent.get_text()
        
        # Generate event ID
        event_id = hashlib.md5(f"pratt_header_{name}".encode()).hexdigest()
        
        return {
            "id": event_id,
            "name": name,
            "description": f"Event at Pratt Institute. {parent_text[:200]}...",
            "start_date": None,
            "end_date": None,
            "location_id": "pratt_institute",
            "community_id": "pratt_institute",
            "category": "academic",
            "url": None,
            "metadata": {
                "source": "pratt_institute",
                "source_group": "Pratt",
                "scraped_at": standardize_datetime(datetime.now()),
                "extraction_method": "header"
            }
        }
        
    except Exception as e:
        print(f"Error extracting header data: {e}")
        return None

def extract_event_from_container(container, base_url):
    """Extract event info from a container element"""
    try:
        # Look for any text that might be an event name
        text_elements = container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span'])
        
        for elem in text_elements:
            text = elem.get_text(strip=True)
            if text and len(text) > 5 and len(text) < 100:
                # This might be an event name
                event_id = hashlib.md5(f"pratt_container_{text}".encode()).hexdigest()
                
                return {
                    "id": event_id,
                    "name": text,
                    "description": f"Event found in container at Pratt Institute",
                    "start_date": None,
                    "end_date": None,
                    "location_id": "pratt_institute",
                    "community_id": "pratt_institute",
                    "category": "academic",
                    "url": None,
                                "metadata": {
                "source": "pratt_institute",
                "source_group": "Pratt",
                "scraped_at": standardize_datetime(datetime.now()),
                "extraction_method": "container"
            }
                }
        
        return None
        
    except Exception as e:
        print(f"Error extracting container data: {e}")
        return None



if __name__ == "__main__":
    events = scrape_pratt_events()
    print(f"Final result: {len(events['events'])} events scraped")
