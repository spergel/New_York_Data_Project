import cloudscraper
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import hashlib
import json
import time
import random
from event_filter import filter_events, get_filter_stats
from category_utils import determine_categories

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_juilliard_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific Juilliard venues
    if any(term in location_str for term in ['peter jay sharp', 'pjs']):
        return "loc_juilliard_sharp"
    if 'morse' in location_str:
        return "loc_juilliard_morse"
    if 'paul hall' in location_str:
        return "loc_juilliard_paul"
    if 'stephanie p. mcclelland' in location_str:
        return "loc_juilliard_mcclelland"
    
    return "loc_juilliard_main"  # Default to main building

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "The Juilliard School",
            "address": "60 Lincoln Center Plaza, New York, NY 10023",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle specific Juilliard venues
    if any(term in location_str.lower() for term in ['peter jay sharp', 'pjs']):
        return {
            "name": "Peter Jay Sharp Theater",
            "address": "155 W 65th St, New York, NY 10023",
            "type": "venue"
        }
    
    if 'morse' in location_str.lower():
        return {
            "name": "Morse Hall",
            "address": "60 Lincoln Center Plaza, New York, NY 10023",
            "type": "venue"
        }
    
    if 'paul hall' in location_str.lower():
        return {
            "name": "Paul Hall",
            "address": "60 Lincoln Center Plaza, New York, NY 10023",
            "type": "venue"
        }
    
    if 'stephanie p. mcclelland' in location_str.lower():
        return {
            "name": "Stephanie P. McClelland Drama Theater",
            "address": "155 W 65th St, New York, NY 10023",
            "type": "venue"
        }
    
    return {
        "name": location_str,
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on title and tags."""
    title = event_data.get('title', '').lower()
    tags = [tag.lower() for tag in event_data.get('tags', [])]
    
    if any(term in title + ' '.join(tags) for term in ['recital', 'concert']):
        return "Performance"
    elif any(term in title + ' '.join(tags) for term in ['master class', 'masterclass']):
        return "Workshop"
    elif any(term in title + ' '.join(tags) for term in ['lecture', 'talk']):
        return "Seminar"
    elif any(term in title + ' '.join(tags) for term in ['opera', 'theater', 'theatre']):
        return "Performance"
    elif any(term in title + ' '.join(tags) for term in ['dance', 'ballet', 'choreography']):
        return "Performance"
    
    return "Performance"  # Default for Juilliard is Performance

def determine_categories_juilliard(event_data):
    """Determine categories for Juilliard events using centralized logic."""
    # Use hybrid approach: tag mapping + keyword analysis
    categories = determine_categories(event_data, method='hybrid')

    # Juilliard-specific categorization
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    tags = event_data.get('tags', [])
    text_content = f"{title} {description} {' '.join(tags)}"
    
    # Check if it's a performance vs discussion/educational event
    performance_keywords = [
        'concert', 'recital', 'performance', 'symphony', 'orchestra', 'chamber',
        'solo', 'ensemble', 'opera', 'ballet', 'musical', 'jazz', 'classical',
        'contemporary', 'world music', 'folk', 'choral', 'vocal', 'instrumental'
    ]
    
    discussion_keywords = [
        'masterclass', 'workshop', 'lecture', 'seminar', 'research', 'study',
        'academic', 'scholarly', 'conference', 'symposium', 'colloquium',
        'musicology', 'music theory', 'composition', 'analysis', 'criticism',
        'history of music', 'ethnomusicology', 'music education', 'pedagogy'
    ]
    
    # Determine if it's performance or discussion
    is_performance = any(keyword in text_content for keyword in performance_keywords)
    is_discussion = any(keyword in text_content for keyword in discussion_keywords)
    
    if is_performance and not is_discussion:
        if 'MUSIC_PERFORMANCE' not in categories:
            categories.append('MUSIC_PERFORMANCE')
    elif is_discussion or not is_performance:
        if 'MUSIC_DISCUSSION' not in categories:
            categories.append('MUSIC_DISCUSSION')
    
    # Check for other performing arts
    if any(term in text_content for term in ['dance', 'ballet', 'choreography', 'theater', 'theatre', 'acting']):
        if 'PERFORMING_ARTS' not in categories:
            categories.append('PERFORMING_ARTS')
    
    # Ensure Juilliard events get EDUCATION category
    if 'EDUCATION' not in categories:
        categories.append('EDUCATION')

    return categories

def fetch_juilliard_events():
    """Try multiple approaches to fetch Juilliard events"""
    
    # Approach 1: Try the main events page directly
    try:
        print("Trying direct approach to Juilliard events page...")
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            },
            delay=10
        )
        
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        url = "https://www.juilliard.edu/events"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        response = scraper.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200 and "Just a moment" not in response.text:
            print("Successfully accessed Juilliard events page")
            return parse_juilliard_html(response.text)
        else:
            print(f"Direct approach failed, status: {response.status_code}")
            
    except Exception as e:
        print(f"Direct approach error: {e}")
    
    # Approach 2: Try the AJAX endpoint with better headers
    try:
        print("Trying AJAX approach with improved headers...")
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            },
            delay=10
        )
        
        time.sleep(random.uniform(2, 4))
        
        url = "https://www.juilliard.edu/views/ajax"
        
        querystring = {
            "_wrapper_format": "drupal_ajax",
            "view_name": "performance_calendar",
            "view_display_id": "block_1",
            "view_args": "",
            "view_path": "/node/4747",
            "view_base_path": "",
            "view_dom_id": "21d160607ab8a63f7868e5e2553121efd4689eaecd9825f235b27b3e83dc6df3",
            "pager_element": "0",
            "page": "0",
            "_drupal_ajax": "1",
            "ajax_page_state[theme]": "juilliard",
            "ajax_page_state[theme_token]": "",
            "ajax_page_state[libraries]": "eJx1kl1u4zAMhC_kxE97HoGWmJgJJQokldZ7-sr56SrY9sWQZwbQ8KMgJRco2wzPw_GkUnzCT2cq1zlpq8DH5-90acEqXl3pcx7OIUquUrB4YIGE-mvwA5fvrPUUMRNomiFGNKOFmHwLWRKOZspUgovwAjrosTe930nmVM6j01R3J8E2qCeJzYK0fRa0N0McNTBs3Rz0M8sCfLiM2dUz_7GVboNGGc4YIlQnKWN4p9GnUQz3uwcnQx-pwC0ktKtL_cnK0nmMIHYuWujvCKGinkQzlLg3YCzpjZFFFeYOL_TEKm8WdoA9vf3Sw3zjN0zdDn0DP0R3xxA0rgGay75iRh-r98XvNf_j8NKtLZl8qqBwVqirvZ7eP-XYSm1LX_aKabLNHPO8gOF0I_yw-f49dkSNn1KgcqJCjuFB4RE5vNTDQ_0C-V0zLg"
        }
        
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.juilliard.edu/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty"
        }
        
        response = scraper.get(url, headers=headers, params=querystring, timeout=30)
        
        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
                if data:
                    print("Successfully fetched AJAX data")
                    return data
            except json.JSONDecodeError:
                print("AJAX response is not valid JSON")
                
    except Exception as e:
        print(f"AJAX approach error: {e}")
    
    print("All approaches failed")
    return []

def parse_juilliard_html(html_content):
    """Parse events from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    events = []
    
    # Look for event articles
    event_articles = soup.find_all('article', class_='event-performance-calendar')
    
    if not event_articles:
        # Try alternative selectors
        event_articles = soup.find_all('div', class_='event-item')
    
    if not event_articles:
        # Try another alternative
        event_articles = soup.find_all('div', class_='views-row')
    
    print(f"Found {len(event_articles)} event articles")
    
    for event in event_articles:
        try:
            # Try different title selectors
            title_elem = event.find('h3') or event.find('h2') or event.find('a')
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                continue
                
            # Try different URL selectors
            url_elem = event.find('a')
            url = 'https://www.juilliard.edu' + url_elem['href'] if url_elem and url_elem.get('href') else ''
            
            # Try different venue selectors
            venue_elem = event.find('div', class_='field--name-field-venue') or event.find('div', class_='venue')
            venue = venue_elem.get_text(strip=True) if venue_elem else ''
            
            # Try different date selectors
            date_elem = event.find('time') or event.find('div', class_='date')
            if date_elem and date_elem.get('datetime'):
                date_str = date_elem['datetime']
                if date_str.endswith('Z'):
                    date_str = date_str[:-1] + '+00:00'
                date = datetime.fromisoformat(date_str)
                end_date = date + timedelta(hours=2)
            else:
                # Try to parse text date
                date_text = date_elem.get_text(strip=True) if date_elem else ''
                if date_text:
                    # Simple date parsing - you might need to adjust this
                    try:
                        date = datetime.strptime(date_text, "%B %d, %Y")
                        end_date = date + timedelta(hours=2)
                    except:
                        continue
                else:
                    continue
            
            # Try different tag selectors
            tags = []
            tag_elems = event.find_all('div', class_='field__item')
            for tag_elem in tag_elems:
                if tag_elem.parent and 'field--name-field-event-tags' in tag_elem.parent.get('class', []):
                    tags.append(tag_elem.get_text(strip=True))
            
            # Create event data
            event_data = {
                "title": title,
                "url": url,
                "venue": venue,
                "date": date,
                "end_date": end_date,
                "tags": tags
            }
            
            events.append(event_data)
            
        except Exception as e:
            print(f"Error parsing event: {e}")
            continue
    
    return events

def parse_juilliard_events(data):
    standardized_events = []
    
    # Handle empty or None data
    if not data:
        print("No data received from Juilliard API")
        return {"events": []}
    
    # If data is already parsed HTML events
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'title' in data[0]:
        for event_data in data:
            try:
                title = event_data.get('title', '')
                url = event_data.get('url', '')
                venue = event_data.get('venue', '')
                date = event_data.get('date')
                end_date = event_data.get('end_date')
                tags = event_data.get('tags', [])
                
                if not title or not date:
                    continue
                
                # Get location details
                location_id = get_location_id(venue)
                venue_obj = standardize_venue(venue)

                # Create event ID using hash of URL and title
                event_id = f"evt_juilliard_{hashlib.md5((url + title).encode()).hexdigest()[:8]}"

                # Create event data for type and category determination
                event_info = {
                    "title": title,
                    "tags": tags
                }

                # Create metadata
                metadata = {
                    "source_url": url,
                    "source_name": "Juilliard Events Calendar",
                    "venue": venue_obj,
                    "organizer": {
                        "name": "The Juilliard School",
                        "type": "organizer"
                    },
                    "additional_info": {
                        "tags": tags
                    }
                }

                standardized_event = {
                    "id": event_id,
                    "name": title,
                    "type": determine_event_type(event_info),
                    "location_id": location_id,
                    "community_id": "com_juilliard",
                    "description": ", ".join(tags),
                    "start_date": date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "category": determine_categories_juilliard(event_info),
                    "source": "juilliard",
                    "source_group": "juilliard",
                    "metadata": metadata
                }

                standardized_events.append(standardized_event)

            except Exception as e:
                print(f"Error processing event: {title if 'title' in locals() else 'Unknown'}. Error: {str(e)}")
                continue
    
    # Original AJAX parsing logic
    else:
        for item in data:
            if item.get('command') == 'insert' and 'data' in item:
                soup = BeautifulSoup(item['data'], 'html.parser')
                
                for event in soup.find_all('article', class_='event-performance-calendar'):
                    try:
                        title = event.find('h3').text.strip() if event.find('h3') else ''
                        url = 'https://www.juilliard.edu' + event.find('a')['href'] if event.find('a') else ''
                        venue = event.find('div', class_='field--name-field-venue').text.strip() if event.find('div', class_='field--name-field-venue') else ''
                        
                        date_time = event.find('time')
                        if not date_time:
                            continue
                            
                        date = datetime.fromisoformat(date_time['datetime'].replace('Z', '+00:00'))
                        end_date = date + timedelta(hours=2)  # Assume 2-hour duration
                        
                        tags = [tag.text for tag in event.find_all('div', class_='field__item') if tag.parent.get('class') == ['field--name-field-event-tags', 'field__items']]

                        # Get location details
                        location_id = get_location_id(venue)
                        venue_obj = standardize_venue(venue)

                        # Create event ID using hash of URL and title
                        event_id = f"evt_juilliard_{hashlib.md5((url + title).encode()).hexdigest()[:8]}"

                        # Create event data for type and category determination
                        event_data = {
                            "title": title,
                            "tags": tags
                        }

                        # Create metadata
                        metadata = {
                            "source_url": url,
                            "source_name": "Juilliard Events Calendar",
                            "venue": venue_obj,
                            "organizer": {
                                "name": "The Juilliard School",
                                "type": "organizer"
                            },
                            "additional_info": {
                                "tags": tags
                            }
                        }

                        standardized_event = {
                            "id": event_id,
                            "name": title,
                            "type": determine_event_type(event_data),
                            "location_id": location_id,
                            "community_id": "com_juilliard",
                            "description": ", ".join(tags),
                            "start_date": date.isoformat(),
                            "end_date": end_date.isoformat(),
                            "category": determine_categories_juilliard(event_data),
                            "source": "juilliard",
                            "source_group": "juilliard",
                            "metadata": metadata
                        }

                        standardized_events.append(standardized_event)

                    except Exception as e:
                        print(f"Error processing event: {title if 'title' in locals() else 'Unknown'}. Error: {str(e)}")
                        continue

        # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")

    return {"events": filtered_events}

def scrape_juilliard_events():
    data = fetch_juilliard_events()
    return parse_juilliard_events(data)

def main():
    events = scrape_juilliard_events()
    print(f"Successfully processed {len(events['events'])} Juilliard events.")
    
    # Save to file for debugging
    if events['events']:
        with open('juilliard_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to juilliard_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()