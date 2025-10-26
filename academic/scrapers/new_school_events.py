import requests
import json
from datetime import datetime, timezone, timedelta
import hashlib
from event_filter import filter_events, get_filter_stats
from category_utils import determine_categories

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_newschool_main"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for specific New School buildings
    if any(term in location_str for term in ['66 w 12', '66 west 12']):
        return "loc_newschool_66w12"
    if any(term in location_str for term in ['63 5th', '63 fifth']):
        return "loc_newschool_63fifth"
    if 'parsons' in location_str:
        return "loc_newschool_parsons"
    if 'arnhold' in location_str:
        return "loc_newschool_arnhold"
    
    return "loc_newschool_main"  # Default to main campus

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str:
        return {
            "name": "The New School",
            "address": "72 5th Ave, New York, NY 10011",
            "type": "venue"
        }
        
    # Handle online venues
    if any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle specific New School buildings
    if any(term in location_str.lower() for term in ['66 w 12', '66 west 12']):
        return {
            "name": "The New School - 66 West 12th Street",
            "address": "66 West 12th Street, New York, NY 10011",
            "type": "venue"
        }
    
    if any(term in location_str.lower() for term in ['63 5th', '63 fifth']):
        return {
            "name": "The New School - 63 Fifth Avenue",
            "address": "63 Fifth Avenue, New York, NY 10003",
            "type": "venue"
        }
    
    if 'parsons' in location_str.lower():
        return {
            "name": "Parsons School of Design",
            "address": "66 Fifth Avenue, New York, NY 10011",
            "type": "venue"
        }
    
    if 'arnhold' in location_str.lower():
        return {
            "name": "Arnhold Hall",
            "address": "55 West 13th Street, New York, NY 10011",
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
    
    if any(term in title + ' '.join(tags) for term in ['seminar', 'colloquium', 'lecture']):
        return "Seminar"
    elif any(term in title + ' '.join(tags) for term in ['workshop', 'training']):
        return "Workshop"
    elif any(term in title + ' '.join(tags) for term in ['conference', 'symposium']):
        return "Conference"
    elif any(term in title + ' '.join(tags) for term in ['performance', 'concert', 'show']):
        return "Performance"
    elif any(term in title + ' '.join(tags) for term in ['exhibition', 'gallery']):
        return "Exhibition"
    
    return "Academic"

def determine_categories_newschool(event_data):
    """Determine categories for New School events using centralized logic."""
    # Use the centralized categorization with keyword analysis
    categories = determine_categories(event_data, method='auto')
    
    # New School-specific categorization
    title = event_data.get('title', '').lower()
    description = event_data.get('description', '').lower()
    tags = event_data.get('tags', [])
    text_content = f"{title} {description} {' '.join(tags)}"
    
    # Check for music events and distinguish performance vs discussion
    # Only apply music categories if the event is actually about music
    if any(term in text_content for term in ['music', 'concert', 'recital', 'orchestra', 'chamber', 'piano', 'violin', 'symphony']):
        # Check if it's a lecture/seminar vs performance
        if any(term in text_content for term in ['lecture', 'seminar', 'masterclass', 'workshop', 'discussion']):
            if 'MUSIC_DISCUSSION' not in categories:
                categories.append('MUSIC_DISCUSSION')
        else:
            if 'MUSIC_PERFORMANCE' not in categories:
                categories.append('MUSIC_PERFORMANCE')
    
    # Check for visual arts events (more specific keywords)
    if any(term in text_content for term in ['exhibition', 'gallery', 'visual', 'design', 'fashion', 'architecture', 'painting', 'sculpture', 'photography']):
        if 'VISUAL_ARTS' not in categories:
            categories.append('VISUAL_ARTS')
    
    # Check for performing arts (theater, dance)
    if any(term in text_content for term in ['theater', 'theatre', 'dance', 'acting', 'drama', 'performance']):
        if 'PERFORMING_ARTS' not in categories:
            categories.append('PERFORMING_ARTS')
    
    # Check for humanities content
    if any(term in text_content for term in ['history', 'literature', 'philosophy', 'classics', 'language', 'anthropology']):
        if 'HUMANITIES' not in categories:
            categories.append('HUMANITIES')
    
    # Check for business/economics content
    if any(term in text_content for term in ['economics', 'business', 'finance', 'capitalism', 'market', 'economy']):
        if 'BUSINESS' not in categories:
            categories.append('BUSINESS')
    
    # Check for social/political content
    if any(term in text_content for term in ['social', 'society', 'community', 'politics', 'policy', 'government', 'exile', 'activism']):
        if 'SOCIAL' not in categories:
            categories.append('SOCIAL')
    
    # Ensure New School events get EDUCATION category
    if 'EDUCATION' not in categories:
        categories.append('EDUCATION')
    
    return categories

def setup_session():
    # Set up the session and headers
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://events.newschool.edu",
        "Referer": "https://events.newschool.edu/",
        "Accept": "application/json"
    })

    # Set up the request URL and parameters
    url = "https://4ep54xkzta-dsn.algolia.net/1/indexes/tns_events/query"
    params = {
        "x-algolia-agent": "Algolia for JavaScript (3.33.0); Browser (lite)",
        "x-algolia-application-id": "4EP54XKZTA",
        "x-algolia-api-key": "2a974f71b015b640c6e692026dddf92c"
    }

    # Get today's date in milliseconds since epoch
    today_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return session, url, params, today_ms

def get_page(session, url, params, today_ms, page_number):
    body = {
        "params": f"filters=(tns_dates>={today_ms})&page={page_number}"
    }
    response = session.post(url, params=params, data=json.dumps(body), headers={"Content-Type": "application/x-www-form-urlencoded"})
    return response.json() if response.status_code == 200 else None

def fetch_new_school_events():
    # Fetch more pages to get November events
    session, url, params, today_ms = setup_session()
    all_events = []
    for page in range(10):  # Increased from 4 to 10 pages
        page_data = get_page(session, url, params, today_ms, page)
        if page_data and 'hits' in page_data:
            events_on_page = page_data['hits']
            all_events.extend(events_on_page)
            print(f"Page {page + 1}: {len(events_on_page)} events")
            
            # Stop if we get an empty page
            if len(events_on_page) == 0:
                print(f"No more events on page {page + 1}, stopping")
                break
        else:
            print(f"Failed to fetch page {page + 1}")
            break
    return all_events

def standardize_new_school_events(events):
    standardized_events = []
    
    for event in events:
        try:
            # Filter out numeric tags
            tags = [tag for tag in event.get('tns_tags', []) if not tag.isdigit()]
            
            # Get location details
            location_str = event.get('location_name', '')
            location_id = get_location_id(location_str)
            venue = standardize_venue(location_str)

            # Create event ID using hash of URL and title
            event_id = f"evt_newschool_{hashlib.md5((event.get('url', '') + event.get('title', '')).encode()).hexdigest()[:8]}"

            # Handle start and end dates
            start_date = event.get('tns_eventStartDate')
            end_date = event.get('tns_eventEndDate')
            
            if not (start_date and end_date):
                continue

            # Convert Unix timestamps to datetime objects
            # The New School API timestamps are already in EST timezone
            # We need to treat them as EST and convert to UTC for storage
            
            from datetime import timezone, timedelta
            est = timezone(timedelta(hours=-5))  # EST is UTC-5
            
            # Convert timestamps assuming they are in EST
            start_datetime = datetime.fromtimestamp(start_date / 1000, tz=est)
            end_datetime = datetime.fromtimestamp(end_date / 1000, tz=est)
            
            # Convert to UTC for consistent storage
            start_datetime = start_datetime.astimezone(timezone.utc)
            end_datetime = end_datetime.astimezone(timezone.utc)
            

            # Create event data for type and category determination
            event_data = {
                "title": event.get('title', ''),
                "description": event.get('description', ''),
                "tags": tags
            }

            # Create metadata
            metadata = {
                "source_url": event.get('url', ''),
                "source_name": "The New School Events",
                "venue": venue,
                "organizer": {
                    "name": "The New School",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": event.get('colleges', []),
                    "tags": tags,
                    "audience": event.get('audience', [])
                }
            }

            standardized_event = {
                "id": event_id,
                "name": event.get('title', ''),
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_newschool",
                "description": event.get('description', ''),
                "start_date": start_datetime.isoformat(),
                "end_date": end_datetime.isoformat(),
                "category": determine_categories_newschool(event_data),
                "source": "new_school",
                "source_group": "Independent",
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {event.get('title', 'Unknown')}. Error: {str(e)}")
            continue

        # Apply event filtering
    print(f"Before filtering: {len(standardized_events)} events")
    
    
    filtered_events = filter_events(standardized_events)
    stats = get_filter_stats(standardized_events, filtered_events)
    print(f"After filtering: {len(filtered_events)} events")
    print(f"Filtering stats: {stats}")

    return {"events": filtered_events}

def scrape_new_school_events():
    raw_events = fetch_new_school_events()
    return standardize_new_school_events(raw_events)

def main():
    events = scrape_new_school_events()
    print(f"Successfully processed {len(events['events'])} New School events.")
    
    # Save to file for debugging
    if events['events']:
        with open('new_school_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to new_school_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()
