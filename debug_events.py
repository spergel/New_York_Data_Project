#!/usr/bin/env python3
import json
import sys

try:
    with open('academic/scrapers/columbia_classics_events_debug.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        events = data.get('events', [])

    print(f'Checking field consistency for first 5 events:')
    for i, event in enumerate(events[:5]):
        print(f'Event {i+1}:')
        print(f'  name: {event.get("name", "MISSING")}')
        print(f'  title: {event.get("title", "MISSING")}')
        print(f'  start_date: {event.get("start_date", "MISSING")}')
        print(f'  source: {event.get("source", "MISSING")}')
        print()

except Exception as e:
    print(f'Error: {e}', file=sys.stderr)



