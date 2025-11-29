#!/usr/bin/env python3
"""
NYU Steinhardt Music Events Scraper
Scrapes music-specific events from NYU Steinhardt music pages
"""

import requests
import json
import re
import hashlib
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from event_filter import filter_events, get_filter_stats
from date_utils import standardize_datetime, create_event_dates

def scrape_nyu_steinhardt_music_events():
    """
    Scrape music events from NYU Steinhardt music pages
    """
    print("Scraping NYU Steinhardt Music events...")
    
    try:
        # Try multiple potential music event pages
        urls_to_try = [
            "https://steinhardt.nyu.edu/music/events",
            "https://steinhardt.nyu.edu/departments/music-performing-arts-professions/events",
            "https://steinhardt.nyu.edu/events?field_event_type_target_id=music",
            "https://steinhardt.nyu.edu/events?field_areas_of_study_target_id=31",  # The Arts
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        all_events = []
        
        for url in urls_to_try:
            try:
                print(f"Trying URL: {url}")
                response = requests.get(url, headers=headers, timeout=30, verify=False)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all event teasers
                event_teasers = soup.find_all('div', class_='teaser')
                print(f"Found {len(event_teasers)} event teasers on {url}")
                
                for teaser in event_teasers:
                    try:
                        # Extract event title
                        title_elem = teaser.find('a', class_='teaser__title-link')
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        event_url = title_elem.get('href', '')
                        if event_url and not event_url.startswith('http'):
                            event_url = f"https://steinhardt.nyu.edu{event_url}"
                        
                        # Skip if we already have this event
                        if any(event['name'] == title for event in all_events):
                            continue
                        
                        # Extract description
                        description = ""
                        desc_elem = teaser.find('p')
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)
                        
                        # Extract location
                        location = "NYU Steinhardt"
                        location_elem = teaser.find('div', class_='teaser__address')
                        if location_elem:
                            location = location_elem.get_text(strip=True)
                        
                        # Extract date information
                        event_date = None
                        time_text = ""
                        
                        # Look for date elements
                        date_elem = teaser.find('div', class_='date')
                        if date_elem:
                            # Extract day name, month, and day
                            day_name = date_elem.find('span', class_='date__day_name')
                            month_elem = date_elem.find('span', class_='date__month')
                            day_elem = date_elem.find('span', class_='date__day')
                            
                            if day_name and month_elem and day_elem:
                                day_name_text = day_name.get_text(strip=True)
                                month_text = month_elem.get_text(strip=True)
                                day_text = day_elem.get_text(strip=True)
                                
                                # Convert month abbreviation to number
                                month_map = {
                                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                                    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                                    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                                }
                                month = month_map.get(month_text.lower())
                                
                                if month:
                                    # Try to determine the year - check if date is in the past
                                    current_year = datetime.now().year
                                    test_date = datetime(current_year, month, int(day_text))
                                    # If the date is more than 6 months in the past, it's probably next year
                                    if test_date < datetime.now() - timedelta(days=180):
                                        event_date = datetime(current_year + 1, month, int(day_text))
                                    else:
                                        event_date = test_date
                        
                        # Extract time information
                        time_elem = teaser.find('span', class_='startend__dates')
                        time_text = ""
                        parsed_start_time = None
                        parsed_end_time = None
                        
                        if time_elem:
                            time_text = time_elem.get_text(strip=True)
                            # Parse time like "8 pm - 9:30 pm" or "8:00 pm - 9:30 pm"
                            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)\s*-\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)', time_text)
                            if time_match:
                                start_hour, start_min, start_period, end_hour, end_min, end_period = time_match.groups()
                                start_min = int(start_min) if start_min else 0
                                end_min = int(end_min) if end_min else 0
                                
                                # Convert start time to 24-hour format
                                start_hour = int(start_hour)
                                if start_period.upper() == 'PM' and start_hour != 12:
                                    start_hour += 12
                                elif start_period.upper() == 'AM' and start_hour == 12:
                                    start_hour = 0
                                parsed_start_time = f"{start_hour:02d}:{start_min:02d}"
                                
                                # Convert end time to 24-hour format
                                end_hour = int(end_hour)
                                if end_period.upper() == 'PM' and end_hour != 12:
                                    end_hour += 12
                                elif end_period.upper() == 'AM' and end_hour == 12:
                                    end_hour = 0
                                parsed_end_time = f"{end_hour:02d}:{end_min:02d}"
                                
                                # Use the full time range for create_event_dates
                                time_text = f"{parsed_start_time} - {parsed_end_time}"
                            else:
                                # Try simpler format like "8 pm" or "8:00 pm"
                                simple_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)', time_text)
                                if simple_match:
                                    hour, minute, period = simple_match.groups()
                                    minute = int(minute) if minute else 0
                                    hour = int(hour)
                                    if period.upper() == 'PM' and hour != 12:
                                        hour += 12
                                    elif period.upper() == 'AM' and hour == 12:
                                        hour = 0
                                    time_text = f"{hour:02d}:{minute:02d}"
                        
                        # If we have a date, create the event
                        if event_date:
                            # Generate unique ID using hash
                            event_id = f"evt_nyu_steinhardt_music_{hashlib.md5((title + event_url + str(event_date)).encode()).hexdigest()[:8]}"
                            
                            # Create standardized dates with proper timezone handling
                            if time_text:
                                # Parse the time range if we have it
                                if parsed_start_time and parsed_end_time:
                                    # Create datetime objects with timezone
                                    start_dt = datetime.combine(event_date.date(), datetime.strptime(parsed_start_time, "%H:%M").time())
                                    end_dt = datetime.combine(event_date.date(), datetime.strptime(parsed_end_time, "%H:%M").time())
                                    
                                    # Assume Eastern Time (EST/EDT)
                                    est = timezone(timedelta(hours=-5))
                                    start_dt = start_dt.replace(tzinfo=est)
                                    end_dt = end_dt.replace(tzinfo=est)
                                    
                                    # Convert to UTC
                                    start_date = start_dt.astimezone(timezone.utc).isoformat()
                                    end_date = end_dt.astimezone(timezone.utc).isoformat()
                                else:
                                    # Use create_event_dates for single time
                                    start_date, end_date = create_event_dates(
                                        event_date.strftime('%Y-%m-%d'), 
                                        time_text, 
                                        duration_hours=1.5
                                    )
                            else:
                                # Default to 7:00 PM EST if no time specified
                                default_time = datetime.combine(event_date.date(), datetime.strptime("19:00", "%H:%M").time())
                                est = timezone(timedelta(hours=-5))
                                default_time = default_time.replace(tzinfo=est)
                                start_date = default_time.astimezone(timezone.utc).isoformat()
                                end_date = (default_time + timedelta(hours=1.5)).astimezone(timezone.utc).isoformat()
                            
                            # Extract areas of study
                            areas_elem = teaser.find('span', class_='fields-inline__content--inline')
                            areas = ""
                            if areas_elem:
                                areas = areas_elem.get_text(strip=True)
                            
                            # Create event object in standard format
                            event = {
                                "id": event_id,
                                "name": title,
                                "type": "Performance",  # Music events are typically performances
                                "location_id": "loc_nyu_steinhardt",
                                "community_id": "com_nyu",
                                "description": description,
                                "start_date": start_date,
                                "end_date": end_date,
                                "category": ["MUSIC_PERFORMANCE", "EDUCATION", "ARTS"],
                                "source": "nyu_steinhardt_music",
                                "source_group": "NYU",
                                "metadata": {
                                    "source_url": event_url,  # Put source_url in metadata for API
                                    "source_name": "NYU Steinhardt Music Events",
                                    "venue": {
                                        "name": location,
                                        "type": "venue"
                                    },
                                    "organizer": {
                                        "name": "NYU Steinhardt",
                                        "type": "organizer"
                                    },
                                    "additional_info": {
                                        "areas_of_study": areas,
                                        "scraped_at": standardize_datetime(datetime.now())
                                    }
                                }
                            }
                            
                            all_events.append(event)
                            print(f"  - {title} ({event_date.strftime('%Y-%m-%d')})")
                        
                    except Exception as e:
                        print(f"Error processing event teaser: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error accessing {url}: {e}")
                continue
        
        print(f"Successfully scraped {len(all_events)} NYU Steinhardt Music events")
        
        # Apply event filtering
        print(f"Before filtering: {len(all_events)} events")
        filtered_events = filter_events(all_events)
        stats = get_filter_stats(all_events, filtered_events)
        print(f"After filtering: {len(filtered_events)} events")
        print(f"Filtering stats: {stats}")
        
        return {"events": filtered_events}
        
    except Exception as e:
        print(f"Error scraping NYU Steinhardt Music events: {e}")
        return {"events": []}

if __name__ == "__main__":
    result = scrape_nyu_steinhardt_music_events()
    print(f"\nScraped {len(result['events'])} events")
    
    # Save debug output
    with open('nyu_steinhardt_music_events_debug.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("Debug output saved to nyu_steinhardt_music_events_debug.json")



