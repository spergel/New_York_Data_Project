#!/usr/bin/env python3
"""
NYU Steinhardt Music Events Scraper
Scrapes music-specific events from NYU Steinhardt music pages
"""

import requests
import json
import re
from datetime import datetime, timedelta
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
                                    # Assume current year for now (could be improved)
                                    current_year = datetime.now().year
                                    event_date = datetime(current_year, month, int(day_text))
                        
                        # Extract time information
                        time_elem = teaser.find('span', class_='startend__dates')
                        if time_elem:
                            time_text = time_elem.get_text(strip=True)
                            # Parse time like "8 pm - 9:30 pm"
                            time_match = re.search(r'(\d{1,2})\s*(am|pm|AM|PM)\s*-\s*(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)', time_text)
                            if time_match:
                                start_hour, start_period, end_hour, end_minute, end_period = time_match.groups()
                                # Convert to 24-hour format for start time
                                start_hour = int(start_hour)
                                if start_period.upper() == 'PM' and start_hour != 12:
                                    start_hour += 12
                                elif start_period.upper() == 'AM' and start_hour == 12:
                                    start_hour = 0
                                time_text = f"{start_hour:02d}:00"
                        
                        # If we have a date, create the event
                        if event_date:
                            # Generate unique ID
                            event_id = f"evt_nyu_steinhardt_music_{hash(title + str(event_date)) % 100000000:08x}"
                            
                            # Create standardized dates
                            if time_text:
                                start_date, end_date = create_event_dates(
                                    event_date.strftime('%Y-%m-%d'), 
                                    time_text, 
                                    duration_hours=1.5  # Default 1.5 hours for events
                                )
                            else:
                                # Default to 7:00 PM if no time specified
                                start_date, end_date = create_event_dates(
                                    event_date.strftime('%Y-%m-%d'), 
                                    "19:00", 
                                    duration_hours=1.5
                                )
                            
                            # Extract areas of study
                            areas_elem = teaser.find('span', class_='fields-inline__content--inline')
                            areas = ""
                            if areas_elem:
                                areas = areas_elem.get_text(strip=True)
                            
                            # Create event object
                            event = {
                                "id": event_id,
                                "name": title,
                                "description": description,
                                "start_date": start_date,
                                "end_date": end_date,
                                "location_id": None,
                                "community_id": None,
                                "category": "music",
                                "url": event_url,
                                "source": "nyu_steinhardt_music",
                                "source_group": "nyu_steinhardt_music",
                                "source_name": "nyusteinhardtmusic",
                                "source_url": event_url,
                                "venue": {
                                    "name": location,
                                    "type": "venue"
                                },
                                "metadata": {
                                    "scraped_at": standardize_datetime(datetime.now()),
                                    "original_source": "NYU Steinhardt Music",
                                    "areas_of_study": areas,
                                    "extraction_method": "html_parsing"
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



