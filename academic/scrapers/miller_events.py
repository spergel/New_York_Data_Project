import requests
import json
from datetime import datetime, timedelta
import pytz
import re

def fetch_events(page):
    url = f"https://www.millertheatre.com/events?page={page}"
    response = requests.get(url)
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
        "title": event['title'],
        "start_date": date.isoformat(),
        "end_date": (date + timedelta(hours=2)).isoformat(),
        "location": "Miller Theatre, Columbia University",
        "description": event.get('subtitle') or event.get('alternativeEventSubtitle') or "",
        "url": event['url'],
        "source": "Miller Theatre",
        "image_url": event['image']['url'],
        "department": "Miller Theatre",
        "university": "Columbia University",
        "tags": ["Performance"] + event['category']['title'].split(',')
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
    # Optionally save to file here if needed for standalone running