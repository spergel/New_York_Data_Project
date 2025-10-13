#!/usr/bin/env python3
import json

# Check each problematic scraper
scrapers_to_check = [
    'gallatin_events_debug.json',
    'isaw_events_debug.json',
    'columbia_events_debug.json'
]

for scraper_file in scrapers_to_check:
    filepath = f'academic/scrapers/{scraper_file}'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            events = data.get('events', [])
            print(f'{scraper_file}: {len(events)} events')

            if events:
                sample = events[0]
                print(f'  Sample source: {sample.get("source")}')
                print(f'  Sample URL: {sample.get("metadata", {}).get("source_url", "No URL")}')
                print(f'  Sample name: {sample.get("name", "No name")[:50]}...')
                print()
    except Exception as e:
        print(f'{scraper_file}: ERROR - {e}')
        print()


