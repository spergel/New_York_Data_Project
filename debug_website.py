#!/usr/bin/env python3
import requests
import json

print("DEBUGGING Academic Events Website")
print("=" * 50)

# Check if server is running
try:
    response = requests.get('http://localhost:8000', timeout=3)
    print(f"Server status: {response.status_code}")
except Exception as e:
    print(f"Server not running: {e}")
    exit(1)

# Check if JSON data is accessible
try:
    json_response = requests.get('http://localhost:8000/scraped_events.json', timeout=3)
    if json_response.status_code == 200:
        data = json_response.json()
        events = data.get('events', [])
        print(f"JSON accessible: {len(events)} events")

        # Check first few events for URLs
        events_with_urls = 0
        for event in events[:10]:
            if event.get('url'):
                events_with_urls += 1
        print(f"Events with URLs in first 10: {events_with_urls}")

        # Show sample event structure
        if events:
            sample = events[0]
            print(f"\nSample event keys: {list(sample.keys())}")
            print(f"Has URL: {'url' in sample and sample['url']}")
            if sample.get('url'):
                print("URL value:", sample['url'][:100] + "...")
            print("Name:", sample.get('name', 'No name')[:50] + "...")
    else:
        print(f"JSON not accessible: {json_response.status_code}")
except Exception as e:
    print(f"JSON error: {e}")

print("\nWebsite should be at: http://localhost:8000")
print("If no URLs found, events might not have URLs in the data")