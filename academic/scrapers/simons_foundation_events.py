import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import pytz
import hashlib

url = "https://www.simonsfoundation.org/wp/wp-admin/admin-ajax.php"

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "cookie": "_ga=GA1.1.1640635026.1727143515; privacy-consent-given=true; A17_fonts_cookie_sans=2; _ga_C1G2F4HXQL=GS1.1.1727622620.5.1.1727622648.32.0.0",
    "origin": "https://www.simonsfoundation.org",
    "referer": "https://www.simonsfoundation.org/flatiron/events/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
}

def get_location_id(location_str):
    """Map location string to standard location ID."""
    if not location_str:
        return "loc_virtual"
    
    location_str = location_str.lower()
    
    # Check for online/virtual events
    if any(term in location_str for term in ['online', 'zoom', 'virtual', 'webinar']):
        return "loc_virtual"
    
    # Check for Simons Foundation building
    if any(term in location_str for term in ['162 5th', '162 fifth', 'simons foundation']):
        return "loc_simons_main"
    
    # Check for Flatiron Institute
    if 'flatiron' in location_str:
        return "loc_simons_flatiron"
    
    return "loc_simons_main"  # Default to main building

def standardize_venue(location_str):
    """Create a standardized Venue object from location string."""
    if not location_str or any(term in location_str.lower() for term in ['online', 'zoom', 'virtual', 'webinar']):
        return {
            "name": "Online Event",
            "type": "virtual"
        }
    
    # Handle Simons Foundation building
    if any(term in location_str.lower() for term in ['162 5th', '162 fifth', 'simons foundation']):
        return {
            "name": "Simons Foundation",
            "address": "162 5th Ave, New York, NY 10010",
            "type": "venue"
        }
    
    # Handle Flatiron Institute
    if 'flatiron' in location_str.lower():
        return {
            "name": "Flatiron Institute",
            "address": "162 5th Ave, New York, NY 10010",
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
    elif any(term in title + ' '.join(tags) for term in ['meeting', 'discussion']):
        return "Meeting"
    
    return "Academic"

def determine_categories(event_data):
    """Map Simons Foundation categories to standard EventCategory enum values."""
    categories = set()
    title = event_data.get('title', '').lower()
    tags = [tag.lower() for tag in event_data.get('tags', [])]
    department = event_data.get('department', '').lower()
    
    # Default category
    categories.add('SCIENCE')
    
    # Add categories based on content
    if any(term in title + ' '.join(tags) + department for term in ['math', 'mathematics', 'theorem']):
        categories.add('MATH')
    if any(term in title + ' '.join(tags) + department for term in ['computer', 'programming', 'software']):
        categories.add('TECH')
    if any(term in title + ' '.join(tags) + department for term in ['physics', 'quantum', 'astrophysics']):
        categories.add('PHYSICS')
    if any(term in title + ' '.join(tags) + department for term in ['biology', 'neuroscience']):
        categories.add('BIOLOGY')
    
    return list(categories)

def fetch_events(month, year):
    payload = f"action=a17_flatiron_filters&data%5Borganization%5D%5B%5D=46693&data%5Borganization%5D%5B%5D=108527&data%5Borganization%5D%5B%5D=110645&data%5Borganization%5D%5B%5D=110647&data%5Borganization%5D%5B%5D=41&data%5Borganization%5D%5B%5D=37593&data%5Borganization%5D%5B%5D=104999&data%5Borganization%5D%5B%5D=105250&data%5Borganization%5D%5B%5D=40&data%5Borganization%5D%5B%5D=110674&data%5Borganization%5D%5B%5D=114703&data%5Borganization%5D%5B%5D=114706&data%5Borganization%5D%5B%5D=20820&data%5Borganization%5D%5B%5D=26704&data%5Borganization%5D%5B%5D=26761&data%5Borganization%5D%5B%5D=110655&data%5Borganization%5D%5B%5D=110657&data%5Borganization%5D%5B%5D=28938&data%5Borganization%5D%5B%5D=46688&data%5Borganization%5D%5B%5D=46734&data%5Borganization%5D%5B%5D=46781&data%5Borganization%5D%5B%5D=110664&data%5Borganization%5D%5B%5D=110666&data%5Borganization%5D%5B%5D=110668&data%5Borganization%5D%5B%5D=110672&data%5Borganization%5D%5B%5D=54588&data%5Borganization%5D%5B%5D=68601&data%5Borganization%5D%5B%5D=98273&data%5Borganization%5D%5B%5D=105774&data%5Borganization%5D%5B%5D=110661&data%5Borganization%5D%5B%5D=106630&data%5Borganization%5D%5B%5D=39&data%5Borganization%5D%5B%5D=44&data%5Borganization%5D%5B%5D=43&data%5Borganization%5D%5B%5D=8668&data%5Borganization%5D%5B%5D=57030&data%5Borganization%5D%5B%5D=68733&data%5Borganization%5D%5B%5D=108067&data%5Borganization%5D%5B%5D=108116&data%5Borganization%5D%5B%5D=112186&data%5Borganization%5D%5B%5D=113897&data%5Borganization%5D%5B%5D=42&data%5Borganization%5D%5B%5D=102977&data%5Borganization%5D%5B%5D=102984&data%5Borganization%5D%5B%5D=102996&data%5Borganization%5D%5B%5D=103002&data%5Borganization%5D%5B%5D=47&data%5Borganization%5D%5B%5D=33189&data%5Borganization%5D%5B%5D=33242&data%5Borganization%5D%5B%5D=33246&data%5Borganization%5D%5B%5D=34535&data%5Borganization%5D%5B%5D=14709&data%5Borganization%5D%5B%5D=33251&data%5Borganization%5D%5B%5D=33261&data%5Borganization%5D%5B%5D=60169&data%5Borganization%5D%5B%5D=14718&data%5Borganization%5D%5B%5D=33268&data%5Borganization%5D%5B%5D=49077&data%5Borganization%5D%5B%5D=49187&data%5Borganization%5D%5B%5D=60398&data%5Borganization%5D%5B%5D=77607&data%5Borganization%5D%5B%5D=14731&data%5Borganization%5D%5B%5D=33297&data%5Borganization%5D%5B%5D=33301&data%5Borganization%5D%5B%5D=37564&data%5Borganization%5D%5B%5D=38647&data%5Borganization%5D%5B%5D=60191&data%5Borganization%5D%5B%5D=33275&data%5Borganization%5D%5B%5D=82402&data%5Borganization%5D%5B%5D=102726&data%5Borganization%5D%5B%5D=46&data%5Borganization%5D%5B%5D=37212&data%5Borganization%5D%5B%5D=41421&data%5Borganization%5D%5B%5D=66629&data%5Borganization%5D%5B%5D=41449&data%5Borganization%5D%5B%5D=69598&data%5Borganization%5D%5B%5D=100239&data%5Borganization%5D%5B%5D=100243&data%5Borganization%5D%5B%5D=40178&data%5Borganization%5D%5B%5D=64743&data%5Borganization%5D%5B%5D=67280&data%5Borganization%5D%5B%5D=72386&data%5Borganization%5D%5B%5D=72395&data%5Borganization%5D%5B%5D=72403&data%5Borganization%5D%5B%5D=69374&data%5Borganization%5D%5B%5D=69378&data%5Borganization%5D%5B%5D=82190&data%5Borganization%5D%5B%5D=82184&data%5Borganization%5D%5B%5D=68462&data%5Borganization%5D%5B%5D=81498&data%5Borganization%5D%5B%5D=89186&data%5Borganization%5D%5B%5D=94223&data%5Borganization%5D%5B%5D=106561&data%5Borganization%5D%5B%5D=38&data%5Bmonth%5D={month}&data%5Byear%5D={year}"

    response = requests.request("POST", url, data=payload, headers=headers)
    return response.json()['html']

def parse_events(html):
    soup = BeautifulSoup(html, 'html.parser')
    event_articles = soup.find_all('article', class_='m-date-item')
    standardized_events = []

    for article in event_articles:
        try:
            title_elem = article.find('h3', class_='m-date-item__title')
            if not title_elem:
                continue

            title = title_elem.text.strip()
            url_elem = title_elem.find('a')
            url = url_elem['href'] if url_elem else "https://www.simonsfoundation.org/flatiron/events/"

            add_cal_div = article.find('div', class_='a-add-cal')
            if not add_cal_div:
                continue

            start_date = add_cal_div.get('data-start')
            end_date = add_cal_div.get('data-end')
            start_time = add_cal_div.get('data-start-time')
            end_time = add_cal_div.get('data-end-time')
            all_day = add_cal_div.get('data-all-day-event') == 'true'

            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%d/%m/%Y %H:%M")
            end_datetime = datetime.strptime(f"{end_date} {end_time}", "%d/%m/%Y %H:%M")

            location_elem = article.find('span', class_='m-date-item__meta-title', string='Where')
            location = location_elem.find_next('span').text.strip() if location_elem else 'Online'

            tag_elem = article.find('span', class_='m-date-item__type')
            tag = tag_elem.text.strip() if tag_elem else ''

            # Get department from title or default to CCA if mentioned
            department = "Center for Computational Astrophysics" if "CCA" in title else "Flatiron Institute"

            # Create event ID using hash of URL and title
            event_id = f"evt_simons_{hashlib.md5((url + title).encode()).hexdigest()[:8]}"

            # Get location details
            location_id = get_location_id(location)
            venue = standardize_venue(location)

            event_data = {
                "title": title,
                "tags": [tag] if tag else [],
                "department": department
            }

            # Create metadata
            metadata = {
                "source_url": url,
                "source_name": "Simons Foundation",
                "venue": venue,
                "organizer": {
                    "name": "Simons Foundation",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": department,
                    "event_type": tag,
                    "all_day": all_day
                }
            }

            standardized_event = {
                "id": event_id,
                "name": title,
                "type": determine_event_type(event_data),
                "location_id": location_id,
                "community_id": "com_simons",
                "description": "",  # No description available in the source
                "start_date": start_datetime.isoformat(),
                "end_date": end_datetime.isoformat(),
                "category": determine_categories(event_data),
                "metadata": metadata
            }

            standardized_events.append(standardized_event)

        except Exception as e:
            print(f"Error processing event: {title if 'title' in locals() else 'Unknown'}. Error: {str(e)}")
            continue

    return standardized_events

def scrape_simons_events():
    all_events = []
    current_date = datetime.now()

    for i in range(3):
        target_date = current_date + timedelta(days=30*i)
        html = fetch_events(target_date.month, target_date.year)
        events = parse_events(html)
        all_events.extend(events)

    # Remove duplicates based on title and start_date
    unique_events = {(e['name'], e['start_date']): e for e in all_events}.values()
    return {"events": list(unique_events)}

def main():
    events = scrape_simons_events()
    print(f"Successfully processed {len(events['events'])} Simons Foundation events.")
    
    # Save to file for debugging
    if events['events']:
        with open('simons_foundation_events_debug.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print("Events saved to simons_foundation_events_debug.json")
    else:
        print("No events were found to save.")

if __name__ == "__main__":
    main()