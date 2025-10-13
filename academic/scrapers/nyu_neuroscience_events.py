#!/usr/bin/env python3
"""
NYU Langone Neuroscience Events Scraper
Scrapes neuroscience events from the NYU Langone RSS feed
"""

import requests
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from event_filter import filter_events, get_filter_stats
from date_utils import standardize_datetime, create_event_dates

def scrape_nyu_neuroscience_events():
    """
    Scrape neuroscience events from NYU Langone RSS feed
    """
    print("Scraping NYU Langone Neuroscience events...")
    
    try:
        # Fetch the RSS feed
        url = "https://www.trumba.com/calendars/nyu-langone-neuroscience.rss"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the RSS feed
        soup = BeautifulSoup(response.content, 'xml')
        events = []
        
        # Find all item elements in the RSS feed
        items = soup.find_all('item')
        print(f"Found {len(items)} events in RSS feed")
        
        for item in items:
            try:
                # Extract basic event information
                title_elem = item.find('title')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                # Extract description
                description_elem = item.find('description')
                description = ""
                if description_elem:
                    # Clean up HTML in description
                    desc_text = description_elem.get_text(strip=True)
                    # Remove extra whitespace and clean up
                    description = re.sub(r'\s+', ' ', desc_text).strip()
                
                # Extract link
                link_elem = item.find('link')
                event_url = link_elem.get_text(strip=True) if link_elem else ""
                
                # Extract date from pubDate or other date fields
                pub_date_elem = item.find('pubDate')
                event_date = None
                
                if pub_date_elem:
                    try:
                        # Parse RFC 2822 date format
                        date_str = pub_date_elem.get_text(strip=True)
                        event_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
                    except ValueError:
                        # Try alternative date parsing
                        try:
                            event_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
                        except ValueError:
                            print(f"Could not parse date: {date_str}")
                            continue
                
                # Look for date information in the description
                if not event_date and description:
                    # Try to extract date from description text
                    date_match = re.search(r'(\w+day),?\s+(\w+)\s+(\d+),?\s+(\d{4})', description)
                    if date_match:
                        try:
                            day_name, month_name, day, year = date_match.groups()
                            # Convert month name to number
                            month_map = {
                                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                                'september': 9, 'october': 10, 'november': 11, 'december': 12
                            }
                            month = month_map.get(month_name.lower())
                            if month:
                                event_date = datetime(int(year), month, int(day))
                        except (ValueError, KeyError):
                            pass
                
                # Look for time information in description
                time_text = ""
                time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)', description)
                if time_match:
                    hour, minute, period = time_match.groups()
                    hour = int(hour)
                    if period.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif period.lower() == 'am' and hour == 12:
                        hour = 0
                    time_text = f"{hour:02d}:{minute}"
                
                # If we have a date, create the event
                if event_date:
                    # Generate unique ID
                    event_id = f"evt_nyu_neuroscience_{hash(title + str(event_date)) % 100000000:08x}"
                    
                    # Create standardized dates
                    if time_text:
                        start_date, end_date = create_event_dates(
                            event_date.strftime('%Y-%m-%d'), 
                            time_text, 
                            duration_hours=1
                        )
                    else:
                        # Default to 12:00 PM if no time specified
                        start_date, end_date = create_event_dates(
                            event_date.strftime('%Y-%m-%d'), 
                            "12:00", 
                            duration_hours=1
                        )
                    
                    # Extract location from description
                    location = "NYU Langone"
                    location_match = re.search(r'NYU Location.*?:\s*([^<]+)', description, re.IGNORECASE)
                    if location_match:
                        location = location_match.group(1).strip()
                    
                    # Extract speaker information
                    speaker_info = ""
                    speaker_match = re.search(r'Speaker.*?:\s*([^<]+)', description, re.IGNORECASE)
                    if speaker_match:
                        speaker_info = speaker_match.group(1).strip()
                    
                    # Create event object
                    event = {
                        "id": event_id,
                        "name": title,
                        "description": description,
                        "start_date": start_date,
                        "end_date": end_date,
                        "location_id": None,
                        "community_id": None,
                        "category": "neuroscience",
                        "url": event_url,
                        "source": "nyu_neuroscience",
                        "source_group": "nyu_neuroscience",
                        "source_name": "nyulangone",
                        "source_url": event_url,
                        "venue": {
                            "name": location,
                            "type": "venue"
                        },
                        "metadata": {
                            "scraped_at": standardize_datetime(datetime.now()),
                            "original_source": "NYU Langone Neuroscience",
                            "speaker": speaker_info,
                            "extraction_method": "rss_feed"
                        }
                    }
                    
                    events.append(event)
                    print(f"  - {title} ({event_date.strftime('%Y-%m-%d')})")
                
            except Exception as e:
                print(f"Error processing event item: {e}")
                continue
        
        print(f"Successfully scraped {len(events)} NYU Neuroscience events")
        
        # Apply event filtering
        print(f"Before filtering: {len(events)} events")
        filtered_events = filter_events(events)
        stats = get_filter_stats(events, filtered_events)
        print(f"After filtering: {len(filtered_events)} events")
        print(f"Filtering stats: {stats}")
        
        return {"events": filtered_events}
        
    except Exception as e:
        print(f"Error scraping NYU Neuroscience events: {e}")
        return {"events": []}

if __name__ == "__main__":
    result = scrape_nyu_neuroscience_events()
    print(f"\nScraped {len(result['events'])} events")
    
    # Save debug output
    with open('nyu_neuroscience_events_debug.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("Debug output saved to nyu_neuroscience_events_debug.json")
