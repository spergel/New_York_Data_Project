import requests
import re
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os

# Add the scrapers directory to the path to import event_filter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from event_filter import filter_events
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
	"business",
	"finance",
	"economics",
	"management",
]

DATE_REGEXES = [
	# e.g., September 18, 2025
	re.compile(r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})"),
	# e.g., Sep 18, 2025
	re.compile(r"([A-Z][a-z]{2}\.?\s+\d{1,2},\s+\d{4})"),
]

BASE_URL = "https://stern.nyu.edu/events"


def extract_first_date(text: str) -> Optional[str]:
	if not text:
		return None
	
	# First, find the date
	date_parsed = None
	for rx in DATE_REGEXES:
		m = rx.search(text)
		if m:
			try:
				# Normal date format
				date_parsed = datetime.strptime(m.group(1), "%B %d, %Y") if "," in m.group(1) and len(m.group(1).split()[0]) > 3 else None
				if date_parsed:
					break
			except Exception:
				pass
	
	if not date_parsed:
		return None
	
	# Now try to find a time in the text
	# Look for patterns like "7:30 PM" or "2:00 PM"
	time_pattern = re.compile(r'(\d{1,2}):(\d{2})\s*(AM|PM)', re.IGNORECASE)
	time_match = time_pattern.search(text)
	
	if time_match:
		hour = int(time_match.group(1))
		minute = int(time_match.group(2))
		am_pm = time_match.group(3).upper()
		
		# Convert to 24-hour format
		if am_pm == 'PM' and hour != 12:
			hour += 12
		elif am_pm == 'AM' and hour == 12:
			hour = 0
		
		dt_with_tz = create_nyc_datetime(date_parsed.year, date_parsed.month, date_parsed.day, hour, minute)
	else:
		# If no time found, use default 9 AM
		dt_with_tz = create_nyc_datetime(date_parsed.year, date_parsed.month, date_parsed.day, 9, 0)
	
	return standardize_datetime(dt_with_tz)


def is_academic_title(title: str) -> bool:
	t = title.lower()
	return any(k in t for k in ACADEMIC_KEYWORDS)


def scrape_nyu_stern_events() -> Dict[str, List[Dict]]:
	resp = requests.get(BASE_URL, timeout=30)
	resp.raise_for_status()
	soup = BeautifulSoup(resp.text, "html.parser")

	events: List[Dict] = []

	# Strategy: Find header elements that contain academic event titles
	headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
	for h in headers:
		title = (h.get_text() or "").strip()
		if not title:
			continue
		if not is_academic_title(title):
			continue

		# Find a local container to search for date/description
		container = h.parent if h.parent else h
		container_text = " ".join(container.stripped_strings)
		date_iso = extract_first_date(container_text)

		# Build description from nearby text
		desc_parts: List[str] = []
		# Look at a few following siblings for paragraphs
		sib = h.find_next_sibling()
		steps = 0
		while sib is not None and steps < 5:
			text = (sib.get_text() or "").strip()
			if text:
				desc_parts.append(text)
			sib = sib.find_next_sibling()
			steps += 1

		description = "\n\n".join(desc_parts)[:2000]

		# Create deterministic ID from title + base url
		uid = hashlib.md5(f"{BASE_URL}::{title}".encode("utf-8")).hexdigest()[:10]

		events.append({
			"id": f"evt_nyu_stern_{uid}",
			"name": title,
			"description": description,
			"start_date": date_iso or "",
			"end_date": "",
			"source": "nyu",
			"source_group": "nyu_stern",
			"metadata": {
				"source_url": BASE_URL,
				"source_name": "NYU Stern School of Business",
				"venue": {
					"name": "NYU Stern",
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

	# Apply filtering to remove past events and unwanted content
	filtered_events = filter_events(deduped)

	return {"events": filtered_events}


def main():
	try:
		result = scrape_nyu_stern_events()
		print(f"NYU Stern events scraped: {len(result.get('events', []))}")
		# Save debug file
		if result.get("events"):
			import json
			with open("nyu_stern_events_debug.json", "w", encoding="utf-8") as f:
				json.dump(result, f, ensure_ascii=False, indent=2)
	except Exception as e:
		print(f"Error scraping NYU Stern: {e}")


if __name__ == "__main__":
	main()
