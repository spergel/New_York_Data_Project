import requests
import re
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import time
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
    "law",
    "legal",
    "judicial",
    "court",
    "regulation",
    "policy",
]

NON_ACADEMIC_KEYWORDS = [
    "graduation",
    "commencement",
    "orientation",
    "move-in",
    "move out",
    "alumni",
    "reunion",
    "celebration",
    "party",
]

DATE_REGEXES = [
    # e.g., September 18, 2025
    re.compile(r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})"),
    # e.g., Sep 18, 2025
    re.compile(r"([A-Z][a-z]{2}\.?\s+\d{1,2},\s+\d{4})"),
]

BASE_URL = "https://law.nyu.edu/events"


def extract_first_date(text: str) -> Optional[str]:
    if not text:
        return None
    for rx in DATE_REGEXES:
        m = rx.search(text)
        if m:
            try:
                # Normal date format
                parsed = datetime.strptime(m.group(1), "%B %d, %Y") if "," in m.group(1) and len(m.group(1).split()[0]) > 3 else None
                if parsed:
                    # Create timezone-aware datetime in NYC timezone with default 9 AM time
                    dt_with_tz = create_nyc_datetime(parsed.year, parsed.month, parsed.day, 9, 0)
                    return standardize_datetime(dt_with_tz)
            except Exception:
                pass
    return None


def is_academic_title(title: str) -> bool:
    t = title.lower()
    
    # Check for non-academic keywords first
    if any(k in t for k in NON_ACADEMIC_KEYWORDS):
        return False
    
    # Check for academic keywords
    return any(k in t for k in ACADEMIC_KEYWORDS)


def extract_event_description(event_url: str) -> str:
    """Extract description from individual event page"""
    try:
        resp = requests.get(event_url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for description in various possible locations
        description_selectors = [
            ".event-description",
            ".event-content",
            ".entry-content",
            ".event-details",
            ".event-body",
            ".content",
            ".description",
            "article p",
            ".event-description p",
            ".event-content p",
        ]
        
        for selector in description_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                text = desc_elem.get_text().strip()
                if text and len(text) > 20:  # Make sure it's substantial
                    return text
        
        # Fallback: look for any paragraph with substantial content
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 50:  # Substantial paragraph
                return text
        
        return ""
    except Exception as e:
        print(f"Error extracting description from {event_url}: {e}")
        return ""


def scrape_nyu_law_events() -> Dict[str, List[Dict]]:
    resp = requests.get(BASE_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    events: List[Dict] = []

    # Find all event elements - try different selectors
    event_selectors = [
        "article.event",
        ".event-item",
        ".event",
        "article",
        ".event-list article",
        ".events article",
    ]
    
    event_elements = []
    for selector in event_selectors:
        elements = soup.select(selector)
        if elements:
            event_elements = elements
            print(f"Found {len(elements)} events using selector: {selector}")
            break
    
    if not event_elements:
        # Fallback: look for any header with academic keywords
        headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        event_elements = [h.parent for h in headers if h.parent and is_academic_title(h.get_text().strip())]
        print(f"Fallback: Found {len(event_elements)} potential events from headers")

    for element in event_elements:
        # Extract title from various possible locations
        title = ""
        event_url = ""
        
        # Try to find title in header elements
        title_elem = element.find(["h1", "h2", "h3", "h4", "h5", "h6"])
        if title_elem:
            title_link = title_elem.find("a")
            if title_link:
                title = title_link.get_text().strip()
                event_url = title_link.get("href", "")
            else:
                title = title_elem.get_text().strip()
        
        # If no title found, try other selectors
        if not title:
            title_link = element.find("a")
            if title_link:
                title = title_link.get_text().strip()
                event_url = title_link.get("href", "")
        
        if not title or not is_academic_title(title):
            continue

        # Extract date - try various methods
        date_iso = ""
        
        # Look for datetime attribute
        datetime_elem = element.find("time")
        if datetime_elem:
            datetime_attr = datetime_elem.get("datetime", "")
            if datetime_attr:
                try:
                    parsed_date = datetime.fromisoformat(datetime_attr.split("T")[0])
                    # Create timezone-aware datetime in NYC timezone with default 9 AM time
                    dt_with_tz = create_nyc_datetime(parsed_date.year, parsed_date.month, parsed_date.day, 9, 0)
                    date_iso = standardize_datetime(dt_with_tz)
                except:
                    pass
        
        # If no datetime attribute, try to extract from text
        if not date_iso:
            element_text = element.get_text()
            date_iso = extract_first_date(element_text) or ""

        # Extract description from individual event page
        description = ""
        if event_url:
            # Make sure URL is absolute
            if event_url.startswith("/"):
                event_url = "https://law.nyu.edu" + event_url
            elif not event_url.startswith("http"):
                event_url = "https://law.nyu.edu/" + event_url
                
            print(f"Fetching description for: {title[:50]}...")
            description = extract_event_description(event_url)
            time.sleep(1)  # Be respectful to the server

        # Create deterministic ID from title + base url
        uid = hashlib.md5(f"{BASE_URL}::{title}".encode("utf-8")).hexdigest()[:10]

        events.append({
            "id": f"evt_nyu_law_{uid}",
            "name": title,
            "description": description,
            "start_date": date_iso,
            "end_date": "",
            "source": "nyu",
            "source_group": "nyu_law",
            "metadata": {
                "source_url": event_url or BASE_URL,
                "source_name": "NYU School of Law",
                "venue": {
                    "name": "NYU Law",
                    "type": "Offline"
                }
            }
        })

    # Deduplicate by name
    seen = set()
    deduped: List[Dict] = []
    for e in events:
        key = e["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    return {"events": deduped}


def main():
    try:
        result = scrape_nyu_law_events()
        print(f"NYU Law events scraped: {len(result.get('events', []))}")
        
        # Show some examples
        for i, event in enumerate(result.get('events', [])[:3]):
            print(f"\nEvent {i+1}: {event['name']}")
            print(f"Date: {event['start_date']}")
            print(f"Description: {event['description'][:100]}...")
        
        # Save debug file
        if result.get("events"):
            import json
            with open("nyu_law_events_improved_debug.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error scraping NYU Law: {e}")


if __name__ == "__main__":
    main()
