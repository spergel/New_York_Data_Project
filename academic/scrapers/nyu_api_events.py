import requests
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import json
from event_filter import filter_events, get_filter_stats
from date_utils import standardize_datetime, create_nyc_datetime, NY_TZ

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
    "film",
    "performance",
    "theater",
    "concert",
    "community",
    "ceremony",
    "open house",
    "screening",
    "discussion",
    "conversation",
    "stem cells",
    "rediscovering",
    "fanon",
    "service",
    "volunteer",
    "orientation",
    "exchange",
    "visitor",
    "jewish",
    "greek",
    "guide",
]

NON_ACADEMIC_KEYWORDS = [
    "grand rounds",
    "medical center",
    "hospital",
    "clinical",
    "patient",
    "healthcare",
    "medicine",
    "nursing",
    "pharmacy",
    "dental",
    "medical school",
    "irving medical center",
    "cumc",
    "newyork-presbyterian",
    "nyp",
    "health",
    "wellness",
    "fitness",
    "sports",
    "athletics",
    "recreation",
    "dining",
    "housing",
    "residential",
    "admissions",
    "enrollment",
    "registration",
    "orientation",
    "graduation",
    "commencement",
    "alumni",
    "development",
    "fundraising",
    "donation",
    "parking",
    "transportation",
    "shuttle",
    "bus",
    "subway",
    "metro",
    "club fest",
    "sigma chi",
    "pet photo contest",
    "faculty housing",
    "labor day",
    "fall classes begin",
    "gph club training",
    "info table",
    "tabling",
]

BASE_NYU_API_URL = "https://events.nyu.edu/live/calendar/view/all/categories/Open%20to%20the%20Public"


def parse_timestamp(timestamp: int) -> Optional[str]:
    """Parse Unix timestamp to ISO date"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        # Create timezone-aware datetime in NYC timezone
        dt_with_tz = create_nyc_datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        return standardize_datetime(dt_with_tz)
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
    
    # Remove HTML tags and entities
    description = re.sub(r'<[^>]+>', '', description)
    description = description.replace('\\n', ' ')
    description = description.replace('\\/', '/')
    description = description.replace('\\"', '"')
    description = description.replace('\\u2019', "'")
    description = description.replace('\\u201c', '"')
    description = description.replace('\\u201d', '"')
    description = description.replace('\\u2013', '–')
    description = description.replace('\\u2014', '—')
    
    # Remove common calendar links
    description = re.sub(r'https?://[^\s]+', '', description)
    description = re.sub(r'Add to Google Calendar.*', '', description, flags=re.IGNORECASE)
    description = re.sub(r'Add to Outlook.*', '', description, flags=re.IGNORECASE)
    description = re.sub(r'Add to Apple Calendar.*', '', description, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    description = re.sub(r'\s+', ' ', description).strip()
    
    return description


def get_nyu_api_url(page: int = 1) -> str:
    """Generate NYU API URL with pagination"""
    params = {
        'user_tz': 'America/Detroit',
        'template_vars': 'id,href,title,image_src,date_title,time,title_link,location,latitude,longitude,summary,is_canceled,repeats,is_multi_day,is_first_multi_day,multi_day_span,tag_classes,category_classes,is_online,has_map',
        'syntax': '<widget type="events_calendar"><arg id="modular_true">true</arg><arg id="mini_cal_heat_map">false</arg><arg id="search_all_events_only">true</arg><arg id="include_featured_content">true</arg><arg id="thumb_width">430</arg><arg id="thumb_height">300</arg><arg id="hide_repeats">true</arg><arg id="show_groups">true</arg><arg id="show_locations">true</arg><arg id="show_tags">true</arg><arg id="feed_base_path">http://www.nyu.edu/feeds/events</arg></widget>',
        'page': page
    }
    
    # Build URL with parameters
    url = BASE_NYU_API_URL + "?"
    url += "&".join([f"{k}={v}" for k, v in params.items()])
    return url


def scrape_nyu_api_events() -> Dict[str, List[Dict]]:
    """Scrape NYU events from API with pagination"""
    try:
        print("📅 Fetching NYU events from API...")
        events: List[Dict] = []
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            print(f"📄 Fetching page {page}...")
            url = get_nyu_api_url(page)
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            
            data = resp.json()
            
            # Update total pages on first request
            if page == 1:
                total_pages = (data.get('event_count', 0) + data.get('per_page', 50) - 1) // data.get('per_page', 50)
                print(f"📊 Total pages: {total_pages}")
            
            # Extract events from the response
            if 'events' in data:
                for date_key, day_events in data['events'].items():
                    if isinstance(day_events, list):
                        for event in day_events:
                            if not isinstance(event, dict):
                                continue
                                
                            title = event.get('title', '').strip()
                            if not title:
                                continue
                            
                            # Skip non-academic events
                            if not is_academic_title(title):
                                continue
                            
                            # Parse date
                            ts_start = event.get('ts_start')
                            if not ts_start:
                                continue
                            start_date = parse_timestamp(ts_start)
                            if not start_date:
                                continue
                            
                            # Get description and clean it
                            description = clean_description(event.get('summary', ''))
                            
                            # Get location
                            location = event.get('location', 'NYU')
                            if not location:
                                location = 'NYU'
                            
                            # Get URL
                            href = event.get('href', '')
                            if href and not href.startswith('http'):
                                href = f"https://events.nyu.edu/live/event/{href}"
                            elif not href:
                                href = "https://events.nyu.edu/"
                            
                            # Create event ID
                            uid = hashlib.md5(f"nyu_api::{title}::{start_date}".encode("utf-8")).hexdigest()[:10]
                            
                            events.append({
                                "id": f"evt_nyu_api_{uid}",
                                "name": title,
                                "description": description,
                                "start_date": start_date,
                                "end_date": start_date,  # API doesn't provide end dates
                                "source": "nyu",
                                "source_group": "nyu",
                                "metadata": {
                                    "source_url": href,
                                    "source_name": "New York University",
                                    "venue": {
                                        "name": location,
                                        "type": "Offline"
                                    }
                                }
                            })
            
            page += 1
        
        print(f"✅ Found {len(events)} academic events from NYU API")
        
        # Deduplicate by name and date
        seen = set()
        deduped: List[Dict] = []
        for e in events:
            key = f"{e['name'].lower()}_{e['start_date']}"
            if key in seen:
                continue
            seen.add(key)
            deduped.append(e)
        
        # Apply event filtering
        print(f"Before filtering: {len(deduped)} events")
        filtered_events = filter_events(deduped)
        stats = get_filter_stats(deduped, filtered_events)
        print(f"After filtering: {len(filtered_events)} events")
        print(f"Filtering stats: {stats}")
        
        return {"events": filtered_events}
        
    except Exception as e:
        print(f"❌ Error scraping NYU API: {e}")
        return {"events": []}


def main():
    """Main function to run the scraper"""
    try:
        result = scrape_nyu_api_events()
        print(f"📊 NYU API events scraped: {len(result.get('events', []))}")
        
        # Show some examples
        for i, event in enumerate(result.get('events', [])[:3]):
            print(f"\nEvent {i+1}: {event['name']}")
            print(f"Date: {event['start_date']}")
            print(f"Location: {event['metadata']['venue']['name']}")
            print(f"Description: {event['description'][:100]}...")
        
        # Save debug file
        if result.get("events"):
            import json
            with open("nyu_api_events_debug.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("💾 Saved to nyu_api_events_debug.json")
            
    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    main()
