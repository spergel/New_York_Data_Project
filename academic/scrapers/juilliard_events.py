import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import hashlib
import json

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

def determine_categories(event_data):
    """Map Juilliard categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    tags = [tag.lower() for tag in event_data.get('tags', [])]
    
    # Default category
    categories.add('ARTS')
    
    # Add categories based on content
    if any(term in title + ' '.join(tags) for term in ['music', 'concert', 'recital', 'orchestra']):
        categories.add('MUSIC')
    if any(term in title + ' '.join(tags) for term in ['dance', 'ballet', 'choreography']):
        categories.add('DANCE')
    if any(term in title + ' '.join(tags) for term in ['drama', 'theater', 'theatre', 'acting']):
        categories.add('THEATER')
    if any(term in title + ' '.join(tags) for term in ['opera', 'vocal', 'voice']):
        categories.add('MUSIC')
    if any(term in title + ' '.join(tags) for term in ['jazz', 'historical']):
        categories.add('MUSIC')
    
    return list(categories)

def fetch_juilliard_events():
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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def parse_juilliard_events(data):
    standardized_events = []
    
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
                        "category": determine_categories(event_data),
                        "metadata": metadata
                    }

                    standardized_events.append(standardized_event)

                except Exception as e:
                    print(f"Error processing event: {title if 'title' in locals() else 'Unknown'}. Error: {str(e)}")
                    continue

    return {"events": standardized_events}

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