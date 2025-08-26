import requests
import json
import re

def debug_miller_theatre():
    """Debug the Miller Theatre scraper"""
    
    url = "https://www.millertheatre.com/events?page=1"
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        print(f"First 500 chars: {response.text[:500]}")
        
        # Look for the events pattern
        pattern = r'<events :events="(\[.*?\])"'
        match = re.search(pattern, response.text, re.DOTALL)
        
        if match:
            print("Found events pattern!")
            events_json = match.group(1).replace('&quot;', '"')
            print(f"Events JSON (first 200 chars): {events_json[:200]}...")
            
            try:
                events = json.loads(events_json)
                print(f"Successfully parsed {len(events)} events")
                if events:
                    print(f"First event: {events[0]}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        else:
            print("No events pattern found in HTML")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_miller_theatre()
