#!/usr/bin/env python3
import json

# Load the data
with open('events_test/academic_events_filtered.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data['events']

# Check institutions
sources = set(event['source'] for event in events)
print(f"Found {len(sources)} institutions: {sorted(sources)}")

# Check sample events from each institution
for source in sorted(sources):
    source_events = [e for e in events if e['source'] == source]
    print(f"\n{source.upper()} ({len(source_events)} events):")
    for event in source_events[:3]:  # Show first 3 events
        print(f"  - {event['name'][:60]}...")
        print(f"    Date: {event.get('startDate', 'No date')}")
        print(f"    Source group: {event.get('source_group', 'None')}")

# Check date ranges
dates = [e.get('startDate') for e in events if e.get('startDate')]
if dates:
    print(f"\nDate range: {min(dates)} to {max(dates)}")
else:
    print("\nNo dates found!")
