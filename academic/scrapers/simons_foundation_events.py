import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import pytz
import hashlib
import warnings

# URLs for different event series
PRESIDENTIAL_LECTURES_URL = "https://www.simonsfoundation.org/sf-events/?type=simons-foundation-presidential-lectures"
PRESENTS_EVENTS_URL = "https://www.simonsfoundation.org/sf-events/?type=simons-foundation-presents"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    # Cookie kept as it might be necessary for access/consent
    "cookie": "_ga=GA1.1.1640635026.1727143515; privacy-consent-given=true; A17_fonts_cookie_sans=2; _ga_C1G2F4HXQL=GS1.1.1727622620.5.1.1727622648.32.0.0",
    "referer": "https://www.simonsfoundation.org/sf-events/", # Updated referer
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
}

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_virtual" # Default to virtual if no string
    
    location_str = location_str.lower()
    
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    if any(term in location_str for term in ['162 5th', '162 fifth', 'simons foundation', 'flatiron institute', 'gerald d. fischbach auditorium']):
        return "loc_simons_main" # Consolidate Simons/Flatiron to main for lectures
    
    # For Presidential Lectures, if not explicitly virtual, assume main venue
    return "loc_simons_main"

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str or any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # For Presidential Lectures, assume Simons Foundation if not specified as virtual
    # The address is the same for Simons Foundation and Flatiron Institute
    if any(term in location_str.lower() for term in ['gerald d. fischbach auditorium', 'fischbach']):
        return {
            "name": "Gerald D. Fischbach Auditorium, Simons Foundation",
            "address": "162 5th Ave, New York, NY 10010",
            "type": "venue"
        }
        
    return {
        "name": "Simons Foundation",
        "address": "162 5th Ave, New York, NY 10010",
        "type": "venue"
    }

def determine_event_type(event_data):
    """Determine event type based on HTML data or title."""
    html_event_type = event_data.get('html_event_type', '').strip()
    if html_event_type:
        return html_event_type.capitalize() # e.g., "In conversation" -> "In Conversation"
    
    title = event_data.get('title', '').lower()
    if 'lecture' in title: return "Lecture"
    if 'seminar' in title or 'colloquium' in title: return "Seminar"
    if 'workshop' in title: return "Workshop"
    if 'conference' in title or 'symposium' in title: return "Conference"
    if 'conversation' in title or 'discussion' in title: return "Discussion"
    
    return "Event" # Generic fallback

def determine_categories(event_data):
    """Determine categories for Simons Foundation events."""
    categories = set()
    categories.add('SCIENCE') # Core theme of Simons Foundation
    
    title = event_data.get('title', '').lower()
    html_event_type = event_data.get('html_event_type', '').lower()
    
    if 'lecture' in html_event_type or 'lecture' in title:
        categories.add('LECTURE')
    if 'in conversation' in html_event_type or 'discussion' in title:
        categories.add('DISCUSSION')
        categories.add('PUBLIC_ENGAGEMENT')

    if any(term in title for term in ['math', 'mathematics']): categories.add('MATH')
    if any(term in title for term in ['physics', 'quantum', 'astrophysics', 'matter']): categories.add('PHYSICS')
    if any(term in title for term in ['biology', 'neuroscience', 'gene', 'frogs', 'spider', 'brain', 'birds']): categories.add('BIOLOGY')
    if any(term in title for term in ['computing', 'computational']): categories.add('TECH')
    
    return list(categories)

def fetch_events_from_url(url_to_fetch, series_name):
    """Fetch HTML content from a given URL."""
    print(f"Fetching {series_name} events from: {url_to_fetch}")
    try:
        response = requests.get(url_to_fetch, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {series_name} page ({url_to_fetch}): {e}")
        return None

def parse_events(html, series_name):
    if not html:
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    event_articles = soup.find_all('article', class_='m-post--date')
    standardized_events = []
    current_utc_time = datetime.now(pytz.utc)

    for article in event_articles:
        try:
            title_elem = article.find('a', class_='m-post__title')
            if not title_elem: continue
            title = title_elem.text.strip()
            url = title_elem['href']

            time_tag = article.find('time', datetime=True)
            if not time_tag or not time_tag.get('datetime'):
                print(f"Skipping event (missing time attribute): {title}")
                continue

            event_timestamp = int(time_tag['datetime'])
            start_datetime_utc = datetime.fromtimestamp(event_timestamp, tz=pytz.utc)

            if start_datetime_utc < current_utc_time:
                continue # Skip past events

            # Default end time, can be overridden
            end_datetime_utc = start_datetime_utc + timedelta(hours=2)
            
            # Check for specific start/end times in m-post__cal
            cal_div = article.find('div', class_='m-post__cal')
            location_str_from_cal = "Simons Foundation" # Default
            
            if cal_div:
                data_start_time_str = cal_div.get('data-start-time')
                data_end_time_str = cal_div.get('data-end-time')
                data_start_date_str = cal_div.get('data-start') # DD/MM/YYYY
                
                if data_start_time_str and data_start_date_str:
                    try:
                        # Parse date and time from cal_div attributes
                        parsed_start_date = datetime.strptime(data_start_date_str, "%d/%m/%Y").date()
                        parsed_start_time = datetime.strptime(data_start_time_str, "%H:%M").time()
                        start_datetime_utc = pytz.utc.localize(datetime.combine(parsed_start_date, parsed_start_time))
                        
                        if data_end_time_str:
                            parsed_end_time = datetime.strptime(data_end_time_str, "%H:%M").time()
                            # Assume end date is same as start date unless data-end is different and parsed
                            end_datetime_utc = pytz.utc.localize(datetime.combine(parsed_start_date, parsed_end_time))
                        else: # Fallback if only start time is available from cal_div
                            end_datetime_utc = start_datetime_utc + timedelta(hours=2)
                    except ValueError as ve:
                        print(f"Warning: Could not parse time from cal_div for {title}: {ve}. Using default.")
                
                cal_location = cal_div.get('data-location')
                if cal_location:
                    location_str_from_cal = cal_location


            # Speaker information (can be single or multiple)
            speakers = []
            people_div = article.find('div', class_='m-people-multi') # For multiple speakers
            if not people_div: # Try single speaker
                people_div = article.find('div', class_='m-person')
            
            if people_div:
                person_tags = people_div.find_all('div', class_='m-person', recursive=False) # Direct children if m-people-multi
                if not person_tags and people_div.name == 'div' and 'm-person' in people_div.get('class', []): # If people_div itself is m-person
                    person_tags = [people_div]

                for person_tag in person_tags:
                    name_tag = person_tag.find('span', class_='m-person__title')
                    if name_tag:
                        speaker_name = name_tag.get_text(strip=True)
                        affiliation = ""
                        # Attempt to get affiliation more robustly
                        # Affiliation might be directly after the name_tag span, or as part of the parent's text
                        sibling_text = name_tag.next_sibling
                        if sibling_text and isinstance(sibling_text, str) and sibling_text.strip():
                            affiliation = sibling_text.strip().lstrip(',').strip()
                        
                        if not affiliation: # Fallback if not a direct sibling
                            full_text_nodes = [node for node in name_tag.parent.contents if isinstance(node, str)]
                            if len(full_text_nodes) > 0:
                                potential_affiliation = " ".join(node.strip() for node in full_text_nodes).strip()
                                if potential_affiliation.startswith(speaker_name): # Basic check
                                     potential_affiliation = potential_affiliation[len(speaker_name):].strip().lstrip(',').strip()
                                affiliation = potential_affiliation

                        speakers.append({"name": speaker_name, "affiliation": affiliation})

            # Event type, location from m-post__cats
            html_event_type = "Event" # Default
            location_str_from_cats = None
            registration_url = None
            
            cats_div = article.find('div', class_='m-post__cats')
            if cats_div and cats_div.ul:
                list_items = cats_div.ul.find_all('li', recursive=False)
                if list_items:
                    html_event_type = list_items[0].text.strip() # First li is usually type
                    for li in list_items:
                        loc_tag = li.find('a', href=lambda x: x and 'maps.google.com' in x)
                        if loc_tag:
                            location_str_from_cats = loc_tag.text.strip()
                        
                        reg_button = li.find('a', class_='btn--block', string=lambda t: 'Register' in t if t else False)
                        if not reg_button: # Try button within m-block-button
                             block_button_div = li.find('div', class_='m-block-button')
                             if block_button_div:
                                 reg_button = block_button_div.find('a', class_='btn--block')
                        if reg_button and reg_button.has_attr('href'):
                            registration_url = reg_button['href']


            # Determine final location string (prefer more specific if available)
            final_location_str = location_str_from_cats or location_str_from_cal or "Simons Foundation"
            location_id = get_location_id(final_location_str)
            venue = standardize_venue(final_location_str)

            event_id_source = url + title + start_datetime_utc.isoformat()
            event_id = f"evt_simons_{hashlib.md5(event_id_source.encode()).hexdigest()[:12]}" # Longer hash

            event_data_for_typing_cats = {
                "title": title,
                "html_event_type": html_event_type,
                "tags": [html_event_type] if html_event_type else [] 
            }
            
            description_parts = [f"{s['name']} ({s['affiliation']})" for s in speakers if s['name'] and s['affiliation']]
            if not description_parts and speakers: # If affiliation is missing but name is there
                 description_parts = [s['name'] for s in speakers if s['name']]
            
            event_description = "; ".join(description_parts) if description_parts else title

            metadata = {
                "source_url": url,
                "source_name": f"Simons Foundation - {series_name}",
                "venue": venue,
                "organizer": {"name": "Simons Foundation", "type": "organizer"},
                "additional_info": {
                    "department": f"Simons Foundation {series_name} Series",
                    "speakers": speakers if speakers else None,
                    "video_url": None, # Video URL parsing was for a different structure
                    "registration_url": registration_url,
                    "event_source_type": html_event_type
                }
            }
            # Attempt to find video URL if present (might be in different location in this HTML)
            video_link_tag = article.find('a', class_='btn--block', string=lambda t: 'Watch Video' in t if t else False)
            if video_link_tag and video_link_tag.has_attr('href'):
                metadata['additional_info']['video_url'] = video_link_tag['href']


            standardized_event = {
                "id": event_id,
                "name": title,
                "type": determine_event_type(event_data_for_typing_cats),
                "location_id": location_id,
                "community_id": "com_simons",
                "description": event_description,
                "start_date": start_datetime_utc.isoformat(),
                "end_date": end_datetime_utc.isoformat(),
                "category": determine_categories(event_data_for_typing_cats),
                "metadata": metadata,
                "price": {"amount": 0.0, "type": "free"},
                "status": "scheduled",
                "registration_required": bool(registration_url)
            }
            standardized_events.append(standardized_event)

        except Exception as e:
            title_for_error = title if 'title' in locals() and title else 'Unknown Event'
            print(f"Error processing event: {title_for_error} from {series_name}. Error: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    return standardized_events

def scrape_simons_events():
    """Scrape events from multiple Simons Foundation series."""
    all_fetched_events = []
    
    # Simons Foundation Presidential Lectures
    html_presidential = fetch_events_from_url(PRESIDENTIAL_LECTURES_URL, "Presidential Lectures")
    if html_presidential:
        events_presidential = parse_events(html_presidential, "Presidential Lectures")
        all_fetched_events.extend(events_presidential)
        print(f"Parsed {len(events_presidential)} events from Presidential Lectures.")

    # Simons Foundation Presents
    html_presents = fetch_events_from_url(PRESENTS_EVENTS_URL, "Simons Foundation Presents")
    if html_presents:
        events_presents = parse_events(html_presents, "Simons Foundation Presents")
        all_fetched_events.extend(events_presents)
        print(f"Parsed {len(events_presents)} events from Simons Foundation Presents.")

    # Deduplicate events based on ID (since ID is now more unique with timestamp)
    # If IDs are truly unique, this step might be redundant but safe
    unique_events_dict = {event['id']: event for event in all_fetched_events}
    final_unique_events = list(unique_events_dict.values())
    
    print(f"Total unique events fetched: {len(final_unique_events)}")
    return {"events": final_unique_events}

def get_simons_internal_events():
    """
    DEPRECATED: Function to fetch Simons Foundation internal events.
    
    This function is deprecated and will not be called by default.
    It retrieves internal Simons Foundation events that are sometimes open to the public.
    Kept for future reference and potential implementation.
    
    Returns:
        dict: Dictionary containing events data
    """
    warnings.warn(
        "get_simons_internal_events is deprecated and not currently used. "
        "It may be implemented in the future to fetch internal events.", 
        DeprecationWarning, 
        stacklevel=2
    )
    
    # This is just a placeholder. The actual implementation would go here.
    # For now, we return an empty events list
    return {"events": []}


def main():
    events_data = scrape_simons_events()
    num_events = len(events_data.get('events', []))
    print(f"Successfully processed {num_events} Simons Foundation events.")
    
    output_filename = 'simons_foundation_events.json'  # Keep original filename
    if events_data['events']:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)
        print(f"Events saved to {output_filename}")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()