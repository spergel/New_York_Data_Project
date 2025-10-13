#!/usr/bin/env python3
"""
NYU Physics Events Scraper
Scrapes physics events from the NYU Physics events page
"""

import requests
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from event_filter import filter_events, get_filter_stats
from date_utils import standardize_datetime, create_event_dates

def scrape_nyu_physics_events():
    """
    Scrape physics events from NYU Physics events page
    """
    print("Scraping NYU Physics events...")
    
    try:
        # Fetch the events page
        url = "http://physics.nyu.edu/events.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Disable SSL verification for this request
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        events = []
        
        # Find all event divs
        event_divs = soup.find_all('div', class_='div_event')
        print(f"Found {len(event_divs)} events on page")
        
        for div in event_divs:
            try:
                # Extract event ID
                event_id_attr = div.get('id', '')
                event_id = f"evt_nyu_physics_{event_id_attr}" if event_id_attr else f"evt_nyu_physics_{hash(str(div)) % 100000000:08x}"
                
                # Extract date and time from the div text
                div_text = div.get_text()
                
                # Look for date pattern in the entire div text
                date_time_text = ""
                date_match = re.search(r'(\w+)\s+(\d+),\s+(\d{4})\s+\w+\s+(\d{1,2}):(\d{2})\s+(AM|PM)', div_text)
                if date_match:
                    date_time_text = date_match.group(0)
                
                # Parse date and time
                event_date = None
                time_text = ""
                
                # Look for date patterns like "September 10, 2025 Wednesday 2:00 PM"
                date_match = re.search(r'(\w+)\s+(\d+),\s+(\d{4})\s+\w+\s+(\d{1,2}):(\d{2})\s+(AM|PM)', date_time_text)
                if date_match:
                    month_name, day, year, hour, minute, period = date_match.groups()
                    
                    # Convert month name to number
                    month_map = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12
                    }
                    month = month_map.get(month_name.lower())
                    if month:
                        # Convert to 24-hour format
                        hour = int(hour)
                        if period.upper() == 'PM' and hour != 12:
                            hour += 12
                        elif period.upper() == 'AM' and hour == 12:
                            hour = 0
                        
                        event_date = datetime(int(year), month, int(day), hour, int(minute))
                        time_text = f"{hour:02d}:{minute}"
                
                if not event_date:
                    print(f"Could not parse date from: {date_time_text}")
                    continue
                
                # Extract location
                location = "NYU Physics"
                location_links = div.find_all('a', href=True)
                for link in location_links:
                    if 'broadway' in link.get('href', '').lower() or 'meyer' in link.get('href', '').lower():
                        location_text = link.get_text(strip=True)
                        if location_text:
                            location = f"726 {location_text}"
                            break
                
                # Look for room numbers in the text
                room_match = re.search(r'(Room\s+\d+|Meyer\s+\d+)', div.get_text())
                if room_match:
                    location += f", {room_match.group(1)}"
                
                # Extract event type/series
                event_type = ""
                series_links = div.find_all('a', href=True)
                for link in series_links:
                    href = link.get('href', '')
                    if 'EventsPage=' in href:
                        series_text = link.get_text(strip=True)
                        if series_text:
                            event_type = series_text
                            break
                
                # Extract speaker name
                speaker = ""
                speaker_b = div.find('b')
                if speaker_b:
                    speaker_text = speaker_b.get_text(strip=True)
                    # Skip if it's the title (usually in italics)
                    if not speaker_text.startswith('The ') and not speaker_text.startswith('Is '):
                        speaker = speaker_text
                
                # Extract institution
                institution = ""
                speaker_line = speaker_b.parent if speaker_b else None
                if speaker_line:
                    institution_text = speaker_line.get_text(strip=True)
                    # Look for institution after speaker name
                    if speaker and speaker in institution_text:
                        remaining = institution_text.replace(speaker, '').strip()
                        if remaining:
                            institution = remaining
                
                # Extract title
                title = ""
                title_i = div.find('i')
                if title_i:
                    title = title_i.get_text(strip=True)
                
                # If no title found, use speaker and event type
                if not title and speaker:
                    if event_type:
                        title = f"{event_type} - {speaker}"
                    else:
                        title = f"Physics Event - {speaker}"
                
                # Extract description
                description = ""
                abstract_div = div.find('div', class_='abstract')
                if abstract_div:
                    description = abstract_div.get_text(strip=True)
                
                # If no description, create one from available info
                if not description:
                    desc_parts = []
                    if speaker:
                        desc_parts.append(f"Speaker: {speaker}")
                    if institution:
                        desc_parts.append(f"Institution: {institution}")
                    if event_type:
                        desc_parts.append(f"Event Type: {event_type}")
                    description = " | ".join(desc_parts) if desc_parts else "NYU Physics Event"
                
                # Create standardized dates
                start_date, end_date = create_event_dates(
                    event_date.strftime('%Y-%m-%d'), 
                    time_text, 
                    duration_hours=1
                )
                
                # Create event object
                event = {
                    "id": event_id,
                    "name": title,
                    "description": description,
                    "start_date": start_date,
                    "end_date": end_date,
                    "location_id": None,
                    "community_id": None,
                    "category": "physics",
                    "url": f"http://physics.nyu.edu/events.html#{event_id_attr}" if event_id_attr else "",
                    "source": "nyu_physics",
                    "source_group": "nyu_physics",
                    "source_name": "nyuphysics",
                    "source_url": "http://physics.nyu.edu/events.html",
                    "venue": {
                        "name": location,
                        "type": "venue"
                    },
                    "metadata": {
                        "scraped_at": standardize_datetime(datetime.now()),
                        "original_source": "NYU Physics",
                        "speaker": speaker,
                        "institution": institution,
                        "event_type": event_type,
                        "extraction_method": "html_parsing"
                    }
                }
                
                events.append(event)
                print(f"  - {title} ({event_date.strftime('%Y-%m-%d %H:%M')})")
                
            except Exception as e:
                print(f"Error processing event div: {e}")
                continue
        
        print(f"Successfully scraped {len(events)} NYU Physics events")
        
        # Apply event filtering
        print(f"Before filtering: {len(events)} events")
        filtered_events = filter_events(events)
        stats = get_filter_stats(events, filtered_events)
        print(f"After filtering: {len(filtered_events)} events")
        print(f"Filtering stats: {stats}")
        
        return {"events": filtered_events}
        
    except Exception as e:
        print(f"Error scraping NYU Physics events: {e}")
        return {"events": []}

if __name__ == "__main__":
    result = scrape_nyu_physics_events()
    print(f"\nScraped {len(result['events'])} events")
    
    # Save debug output
    with open('nyu_physics_events_debug.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("Debug output saved to nyu_physics_events_debug.json")
