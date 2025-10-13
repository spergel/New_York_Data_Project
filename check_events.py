#!/usr/bin/env python3
import json

with open('academic/scraped_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    events = data.get('events', [])

print(f'Total events: {len(events)}')
print()

# Check first 5 events for URL field
for i, event in enumerate(events[:5]):
    has_url = 'url' in event and event['url']
    print(f'Event {i+1}:')
    print(f'  Name: {event.get("name", "No name")[:60]}...')
    print(f'  Has URL field: {"url" in event}')
    print(f'  URL value: {event.get("url", "None")}')
    print(f'  Metadata keys: {list(event.get("metadata", {}).keys())}')
    print()


