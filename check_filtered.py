#!/usr/bin/env python3
import json
import requests
from datetime import datetime

# Get the filtered events
response = requests.get('http://localhost:8000/scraped_events.json', timeout=3)
data = response.json()
events = data.get('events', [])

# Apply our filtering logic
filtered_events = []
for event in events:
    # Hide events with unknown/missing data
    if not event.get('source') or event.get('source') == 'unknown' or event.get('source') == '':
        continue
    if not event.get('start_date') or event.get('start_date') == '':
        continue
    try:
        # Try to parse the date
        datetime.fromisoformat(event['start_date'].replace('Z', '+00:00'))
        filtered_events.append(event)
    except:
        continue

print(f'Filtered events: {len(filtered_events)}')
print()

# Show sample of filtered events
for i, event in enumerate(filtered_events[:5]):
    print(f'Event {i+1}:')
    print(f'  Title: {event.get("name", "No name")[:50]}...')
    print(f'  Source: {event.get("source", "No source")}')
    print(f'  Date: {event.get("start_date", "No date")}')
    print(f'  Location: {event.get("metadata", {}).get("venue", {}).get("name", "No location")}')
    print()


