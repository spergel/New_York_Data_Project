#!/usr/bin/env python3
import json

# Load the raw data before academic filtering
with open('events_test/all_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data['events']

# Check institutions in raw data
sources = set(event['source'] for event in events)
print(f"Found {len(sources)} institutions in raw data: {sorted(sources)}")

# Check sample events from each institution
for source in sorted(sources):
    source_events = [e for e in events if e['source'] == source]
    print(f"\n{source.upper()} ({len(source_events)} events):")
    for event in source_events[:2]:  # Show first 2 events
        name = event.get('name', event.get('title', 'No name'))
        print(f"  - {name[:60]}...")
        print(f"    Date: {event.get('startDate', 'No date')}")

# Now check what gets filtered out
print(f"\n" + "="*50)
print("ANALYSIS: What gets filtered out by academic filtering")

# Load academic filtered data
with open('events_test/academic_events_filtered.json', 'r', encoding='utf-8') as f:
    academic_data = json.load(f)

academic_events = academic_data['events']
academic_sources = set(event['source'] for event in academic_events)

# Find institutions that get filtered out
filtered_out = sources - academic_sources
kept = sources & academic_sources

print(f"\n✅ KEPT ({len(kept)}): {sorted(kept)}")
print(f"❌ FILTERED OUT ({len(filtered_out)}): {sorted(filtered_out)}")

# Show examples of filtered out events
print(f"\n📋 EXAMPLES OF FILTERED OUT EVENTS:")
for source in sorted(filtered_out):
    source_events = [e for e in events if e['source'] == source]
    print(f"\n{source.upper()} (filtered out):")
    for event in source_events[:3]:
        name = event.get('name', event.get('title', 'No name'))
        print(f"  - {name[:60]}...")
        print(f"    Description: {event.get('description', 'No description')[:80]}...")
