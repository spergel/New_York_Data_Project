#!/usr/bin/env python3
"""
Simons Foundation Events Scraper
Scrapes events from the Simons Foundation website
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import hashlib
from event_filter import filter_events, get_filter_stats
import re

def fetch_simons_events():
    """Fetch events from Simons Foundation website"""
    base_url = "https://www.simonsfoundation.org/sf-events/"
    events = []
    
    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for event articles
        event_articles = soup.find_all('article', class_='m-post')
        
        for article in event_articles[:20]:  # Limit to 20 events
            try:
                event = {}
                
                # Extract title
                title_elem = article.find('a', class_='m-post__title')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                event_url = title_elem.get('href', '')
                
                if not title or len(title) < 10:
                    continue
                
                # Extract date from time element
                time_elem = article.find('time')
                if time_elem:
                    # Get the datetime attribute for Unix timestamp
                    datetime_attr = time_elem.get('datetime')
                    if datetime_attr:
                        try:
                            # Convert Unix timestamp to datetime
                            event_date = datetime.fromtimestamp(int(datetime_attr))
                        except (ValueError, TypeError):
                            event_date = None
                    else:
                        # Fallback: parse the text content
                        date_text = time_elem.get_text(strip=True)
                        event_date = parse_date_text(date_text)
                else:
                    event_date = None
                
                # Extract location from calendar data or location section
                location = "Simons Foundation"
                calendar_div = article.find('div', attrs={'data-behavior': 'calendar_list add_to_calendar'})
                if calendar_div:
                    location = calendar_div.get('data-location', location)
                
                # Extract speaker info
                speaker_elem = article.find('div', class_='m-person')
                speaker_info = ""
                if speaker_elem:
                    speaker_title = speaker_elem.find('span', class_='m-person__title')
                    if speaker_title:
                        speaker_info = speaker_title.get_text(strip=True)
                
                # Create description from available info
                description = f"Simons Foundation Presidential Lecture"
                if speaker_info:
                    description += f" featuring {speaker_info}"
                
                # If we have a valid date, create the event
                if event_date:
                    # Create event ID
                    event_id = f"evt_simons_{hashlib.md5((title + str(event_date)).encode()).hexdigest()[:8]}"
                    
                    event = {
                        "id": event_id,
                        "name": title,
                        "description": description,
                        "start_date": event_date.isoformat(),
                        "end_date": (event_date + timedelta(hours=1)).isoformat(),
                        "source": "simons_foundation",
                        "source_group": "Independent",
                        "metadata": {
                            "source_url": event_url if event_url.startswith('http') else f"https://www.simonsfoundation.org{event_url}",
                            "source_name": "Simons Foundation",
                            "venue": {
                                "name": location,
                                "address": "160 5th Ave, New York, NY 10010",
                                "type": "venue"
                            },
                            "speaker": speaker_info,
                            "event_type": "Presidential Lecture"
                        }
                    }
                    
                    events.append(event)

            except Exception as e:
                print(f"Error processing event article: {e}")
                continue

    except Exception as e:
        print(f"Error fetching Simons Foundation events: {e}")
    
    return events

def parse_date_text(date_text):
    """Parse date text like 'Sep 24' or 'May 14'"""
    try:
        # Handle formats like "Sep 24", "May 14"
        month_abbr = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        parts = date_text.strip().split()
        if len(parts) >= 2:
            month_str = parts[0]
            day_str = parts[1]
            
            if month_str in month_abbr and day_str.isdigit():
                month = month_abbr[month_str]
                day = int(day_str)
                current_year = datetime.now().year
                
                # Create the date
                event_date = datetime(current_year, month, day, 18, 0)  # Default to 6 PM
                
                # If the date is in the past, assume it's for next year
                if event_date < datetime.now():
                    event_date = event_date.replace(year=current_year + 1)
                
                return event_date
    except Exception as e:
        print(f"Error parsing date text '{date_text}': {e}")
    
    return None

def main():
    """Main function"""
    print("Scraping Simons Foundation events...")
    
    try:
        events = fetch_simons_events()
        
        if events:
            # Apply filtering
            print(f"Before filtering: {len(events)} events")
            filtered_events = filter_events(events)
            stats = get_filter_stats(events, filtered_events)
            print(f"After filtering: {len(filtered_events)} events")
            print(f"Filtering stats: {stats}")
            
            # Save to file
            result = {"events": filtered_events}
            with open("simons_foundation_events_debug.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully scraped {len(filtered_events)} Simons Foundation events")
            print("Saved to simons_foundation_events_debug.json")
            
        else:
            print("No events found")
            
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
