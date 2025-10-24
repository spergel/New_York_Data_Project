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
from category_utils import determine_categories
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
                
                # Extract date and time information
                event_date = None
                start_time = None
                end_time = None
                
                # First try to get date from time element with datetime attribute
                time_elem = article.find('time')
                if time_elem:
                    datetime_attr = time_elem.get('datetime')
                    if datetime_attr:
                        try:
                            # Convert Unix timestamp to datetime
                            event_date = datetime.fromtimestamp(int(datetime_attr))
                        except (ValueError, TypeError):
                            event_date = None
                
                # Extract detailed time and location from calendar data
                calendar_div = article.find('div', attrs={'data-behavior': 'calendar_list add_to_calendar'})
                if calendar_div:
                    # Get start and end dates
                    start_date_str = calendar_div.get('data-start', '')
                    end_date_str = calendar_div.get('data-end', '')
                    start_time_str = calendar_div.get('data-start-time', '')
                    end_time_str = calendar_div.get('data-end-time', '')
                    
                    if start_date_str and start_time_str:
                        try:
                            # Parse date in format "05/11/2025" (DD/MM/YYYY)
                            day, month, year = start_date_str.split('/')
                            hour, minute = start_time_str.split(':')
                            
                            event_date = datetime(int(year), int(month), int(day), int(hour), int(minute))
                            
                            # Set end time if available
                            if end_time_str:
                                end_hour, end_minute = end_time_str.split(':')
                                end_date = datetime(int(year), int(month), int(day), int(end_hour), int(end_minute))
                            else:
                                end_date = event_date + timedelta(hours=1)
                                
                        except (ValueError, TypeError) as e:
                            print(f"Error parsing calendar data: {e}")
                            # Fallback to Unix timestamp if available
                            if time_elem and time_elem.get('datetime'):
                                try:
                                    event_date = datetime.fromtimestamp(int(time_elem.get('datetime')))
                                    end_date = event_date + timedelta(hours=1)
                                except:
                                    event_date = None
                                    end_date = None
                
                # If we still don't have a date, try parsing from time element text
                if not event_date and time_elem:
                    date_text = time_elem.get_text(strip=True)
                    event_date = parse_date_text(date_text)
                    if event_date:
                        end_date = event_date + timedelta(hours=1)
                
                # Extract location from calendar data or location section
                location = "Gerald D. Fischbach Auditorium"  # Default location
                if calendar_div:
                    location = calendar_div.get('data-location', location)
                else:
                    # Try to find location in the categories section
                    location_elem = article.find('li', class_='m-post__location')
                    if location_elem:
                        location_link = location_elem.find('a')
                        if location_link:
                            location = location_link.get_text(strip=True)
                
                # Extract speaker info
                speaker_elem = article.find('div', class_='m-person')
                speaker_info = ""
                speaker_title = ""
                if speaker_elem:
                    speaker_title_elem = speaker_elem.find('span', class_='m-person__title')
                    if speaker_title_elem:
                        speaker_title = speaker_title_elem.get_text(strip=True)
                    
                    # Get the full speaker info (title + description)
                    speaker_text = speaker_elem.get_text(strip=True)
                    if speaker_text:
                        speaker_info = speaker_text
                
                # Extract event type from categories
                event_type = "Presidential Lecture"
                categories_ul = article.find('div', class_='m-post__cats')
                if categories_ul:
                    category_items = categories_ul.find_all('li')
                    for item in category_items:
                        if item.get_text(strip=True) == "Lecture":
                            event_type = "Presidential Lecture"
                            break
                
                # Create description from available info
                description = f"Simons Foundation {event_type}"
                if speaker_info:
                    description += f" featuring {speaker_info}"
                
                # If we have a valid date, create the event
                if event_date:
                    # Create event ID
                    event_id = f"evt_simons_{hashlib.md5((title + str(event_date)).encode()).hexdigest()[:8]}"
                    
                    # Prepare event data for categorization
                    event_data = {
                        "name": title,
                        "description": description,
                        "title": title  # Some categorization functions expect 'title' field
                    }
                    
                    # Determine categories
                    categories = determine_categories_simons(event_data)
                    
                    event = {
                        "id": event_id,
                        "name": title,
                        "description": description,
                        "start_date": event_date.isoformat(),
                        "end_date": end_date.isoformat() if end_date else (event_date + timedelta(hours=1)).isoformat(),
                        "category": categories,
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
                            "speaker_title": speaker_title,
                            "event_type": event_type
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

def determine_categories_simons(event_data):
    """Determine categories for Simons Foundation events using centralized logic."""
    # Use the centralized categorization with keyword analysis
    categories = determine_categories(event_data, method='auto')
    
    # Simons Foundation events are typically science-focused
    if 'SCIENCE' not in categories:
        categories.append('SCIENCE')
    
    # Presidential Lectures are educational events
    if 'EDUCATION' not in categories:
        categories.append('EDUCATION')
    
    # Check for specific science disciplines
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    text_content = f"{title} {description}"
    
    # Check for neuroscience/health content
    if any(term in text_content for term in ['neural', 'brain', 'neuroscience', 'cognitive', 'psychology']):
        if 'HEALTH' not in categories:
            categories.append('HEALTH')
    
    # Check for technology content
    if any(term in text_content for term in ['computation', 'algorithm', 'machine learning', 'ai', 'artificial intelligence']):
        if 'TECH' not in categories:
            categories.append('TECH')
    
    return categories

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
