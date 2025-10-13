import cloudscraper
import json
from datetime import datetime, timedelta
import pytz
import re
import hashlib

def fetch_events(page):
    url = f"https://www.millertheatre.com/events?page={page}"
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    return response.text

def extract_events_data(html_content):
    pattern = r'<events :events="(\[.*?\])"'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        events_json = match.group(1).replace('&quot;', '"')
        try:
            return json.loads(events_json)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return []

def parse_event(event):
    date = datetime.fromtimestamp(int(event['date']['unix']), pytz.UTC)

    return {
        "id": f"evt_miller_{hashlib.md5(event['url'].encode()).hexdigest()[:8]}",
        "name": event['title'],
        "type": "Performance",
        "location_id": "loc_miller_theatre",
        "community_id": "com_miller_theatre",
        "description": event.get('subtitle') or event.get('alternativeEventSubtitle') or "",
        "start_date": date.isoformat(),
        "end_date": (date + timedelta(hours=2)).isoformat(),
        "category": ["ARTS"],
        "source": "miller_theatre",
        "source_group": "Columbia",
        "metadata": {
            "source_url": event['url'],
            "source_name": "Miller Theatre",
            "venue": {
                "name": "Miller Theatre",
                "address": "2960 Broadway, New York, NY 10027",
                "type": "venue"
            },
            "organizer": {
                "name": "Columbia University",
                "type": "organizer"
            },
            "additional_info": {
                "image_url": event['image']['url'],
                "department": "Miller Theatre"
            }
        }
    }

def scrape_miller_theatre_events():
    all_events = []
    for page in range(1, 4):  # Fetch first 3 pages
        html_content = fetch_events(page)
        events = extract_events_data(html_content)
        for event in events:
            all_events.append(parse_event(event))
    return all_events

if __name__ == "__main__":
    events = scrape_miller_theatre_events()
    print(f"Scraped {len(events)} events from Miller Theatre")

    # Save to debug file in standardized format
    result = {"events": events}
    with open('miller_events_debug.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("Events saved to miller_events_debug.json")