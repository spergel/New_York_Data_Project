import requests
import re
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

ACADEMIC_KEYWORDS = [
    "lecture",
    "seminar",
    "colloquium",
    "symposium",
    "talk",
    "keynote",
    "workshop",
    "conference",
    "presentation",
    "discussion",
    "book talk",
    "academic",
    "research",
    "thesis",
    "dissertation",
    "panel",
    "roundtable",
    "forum",
    "exhibition",
    "gallery",
    "museum",
    "theology",
    "spirituality",
    "ignatian",
    "mcginley",
]

NON_ACADEMIC_KEYWORDS = [
    "football",
    "gamewatch",
    "pregame",
    "kayaking",
    "alumni",
    "graduation",
    "commencement",
    "orientation",
    "move-in",
    "move out",
    "registration",
    "enrollment",
    "admissions",
    "financial aid",
    "housing",
    "dining",
    "campus store",
    "bookstore",
    "parking",
    "shuttle",
    "transportation",
]

CALENDAR_URL = "https://calendar.google.com/calendar/ical/6ffcg00hcva5955peqk4o7ho0f91flbm%40import.calendar.google.com/public/basic.ics"


def parse_ics_date(date_str: str) -> Optional[str]:
    """Parse ICS date format to ISO date"""
    try:
        # Remove timezone info if present
        if 'T' in date_str:
            date_str = date_str.split('T')[0]
        elif 'Z' in date_str:
            date_str = date_str.replace('Z', '')
        
        # Parse the date
        dt = datetime.strptime(date_str, '%Y%m%d')
        return dt.date().isoformat()
    except Exception:
        return None


def is_academic_title(title: str) -> bool:
    """Determine if an event is academic based on its title"""
    t = title.lower()
    
    # Check for non-academic keywords first
    if any(k in t for k in NON_ACADEMIC_KEYWORDS):
        return False
    
    # Check for academic keywords
    return any(k in t for k in ACADEMIC_KEYWORDS)


def clean_description(description: str) -> str:
    """Clean and format the description"""
    if not description:
        return ""
    
    # Remove common ICS artifacts
    description = description.replace('\\n', '\n')
    description = description.replace('\\', '')
    
    # Remove common calendar links
    description = re.sub(r'https?://[^\s]+', '', description)
    description = re.sub(r'Add to Google Calendar.*', '', description, flags=re.IGNORECASE)
    description = re.sub(r'Add to Outlook.*', '', description, flags=re.IGNORECASE)
    description = re.sub(r'Add to Apple Calendar.*', '', description, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    description = re.sub(r'\s+', ' ', description).strip()
    
    return description


def scrape_fordham_calendar_events() -> Dict[str, List[Dict]]:
    """Scrape Fordham events from Google Calendar feed"""
    try:
        print("📅 Fetching Fordham events from Google Calendar...")
        resp = requests.get(CALENDAR_URL, timeout=30)
        resp.raise_for_status()
        
        events: List[Dict] = []
        
        # Parse the ICS content
        lines = resp.text.split('\n')
        current_event = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('BEGIN:VEVENT'):
                current_event = {}
            elif line.startswith('END:VEVENT'):
                if current_event.get('summary') and current_event.get('dtstart'):
                    # Check if it's an academic event
                    if is_academic_title(current_event['summary']):
                        # Create event ID
                        uid = hashlib.md5(f"fordham_calendar::{current_event['summary']}::{current_event['dtstart']}".encode("utf-8")).hexdigest()[:10]
                        
                        events.append({
                            "id": f"evt_fordham_calendar_{uid}",
                            "name": current_event['summary'],
                            "description": clean_description(current_event.get('description', '')),
                            "start_date": parse_ics_date(current_event['dtstart']),
                            "end_date": parse_ics_date(current_event.get('dtend', '')),
                            "source": "fordham",
                            "source_group": "fordham",
                            "metadata": {
                                "source_url": current_event.get('url', 'https://www.fordham.edu/events/'),
                                "source_name": "Fordham University",
                                "venue": {
                                    "name": current_event.get('location', 'Fordham University'),
                                    "type": "Offline"
                                }
                            }
                        })
            elif line.startswith('SUMMARY:'):
                current_event['summary'] = line[8:]
            elif line.startswith('DESCRIPTION:'):
                current_event['description'] = line[12:]
            elif line.startswith('DTSTART:'):
                current_event['dtstart'] = line[8:]
            elif line.startswith('DTEND:'):
                current_event['dtend'] = line[6:]
            elif line.startswith('LOCATION:'):
                current_event['location'] = line[9:]
            elif line.startswith('URL:'):
                current_event['url'] = line[4:]
        
        print(f"✅ Found {len(events)} academic events from Fordham calendar")
        
        # Deduplicate by name and date
        seen = set()
        deduped: List[Dict] = []
        for e in events:
            key = f"{e['name'].lower()}_{e['start_date']}"
            if key in seen:
                continue
            seen.add(key)
            deduped.append(e)
        
        return {"events": deduped}
        
    except Exception as e:
        print(f"❌ Error scraping Fordham calendar: {e}")
        return {"events": []}


def main():
    """Main function to run the scraper"""
    try:
        result = scrape_fordham_calendar_events()
        print(f"📊 Fordham calendar events scraped: {len(result.get('events', []))}")
        
        # Show some examples
        for i, event in enumerate(result.get('events', [])[:3]):
            print(f"\nEvent {i+1}: {event['name']}")
            print(f"Date: {event['start_date']}")
            print(f"Description: {event['description'][:100]}...")
        
        # Save debug file
        if result.get("events"):
            import json
            with open("fordham_calendar_events_debug.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("💾 Saved to fordham_calendar_events_debug.json")
            
    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    main()
