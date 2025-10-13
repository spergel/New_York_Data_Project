#!/usr/bin/env python3
import requests

print("Testing Academic Events Website...")
print("=" * 40)

try:
    response = requests.get('http://localhost:8000', timeout=3)
    print(f"Server is running: {response.status_code == 200}")

    json_response = requests.get('http://localhost:8000/scraped_events.json', timeout=3)
    if json_response.status_code == 200:
        data = json_response.json()
        events = data.get('events', [])

        # Count events with URLs
        events_with_urls = 0
        for event in events[:20]:
            if event.get('metadata', {}).get('source_url'):
                events_with_urls += 1

        print(f"Events with URLs: {events_with_urls}/20 in sample")
        if events_with_urls > 0:
            print("SUCCESS: Clickable titles should work!")
        else:
            print("ISSUE: No URLs found in sample events")

        print(f"Total events: {len(events)}")
        print("Website: http://localhost:8000")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure to run: cd academic && python -m http.server 8000")


