#!/usr/bin/env python3
import json

with open('academic/scraped_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    events = data.get('events', [])

# Look for events that might be from The New School or NYU Engineering
# by checking names or other fields
new_school_candidates = []
nyu_eng_candidates = []

for event in events:
    name = event.get('name', '').lower()
    source = event.get('source', '')

    if 'new school' in name or 'parsons' in name or 'eugene lang' in name:
        new_school_candidates.append(event)

    if 'engineering' in name.lower() and 'nyu' in source:
        nyu_eng_candidates.append(event)

print(f'Potential New School events: {len(new_school_candidates)}')
for event in new_school_candidates[:3]:
    print(f'  Name: {event.get("name", "No name")[:60]}...')
    print(f'  Source: {event.get("source")}')
    print(f'  Has URL: {bool(event.get("metadata", {}).get("source_url"))}')

print(f'\\nPotential NYU Engineering events: {len(nyu_eng_candidates)}')
for event in nyu_eng_candidates[:3]:
    print(f'  Name: {event.get("name", "No name")[:60]}...')
    print(f'  Source: {event.get("source")}')
    print(f'  Has URL: {bool(event.get("metadata", {}).get("source_url"))}')

# Also check for events with missing source but that might be from these institutions
missing_source_events = [e for e in events if not e.get('source') or e.get('source') == 'unknown']
print(f'\\nEvents with missing/unknown source: {len(missing_source_events)}')

for event in missing_source_events[:5]:
    name = event.get('name', '').lower()
    if 'new school' in name or 'parsons' in name or 'eugene lang' in name or 'engineering' in name:
        print(f'  Missing source event: {event.get("name", "No name")[:50]}...')
