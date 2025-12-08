import requests
import re
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional
from date_utils import standardize_datetime

NY_TZ = ZoneInfo("America/New_York")

ACADEMIC_KEYWORDS = [
	"lecture",
	"seminar",
	"colloquium",
	"symposium",
	"talk",
	"keynote",
	"workshop",
	"conference",
	"exhibition",
	"comedy",
	"artists",
	"books",
]

DATE_REGEXES = [
	# e.g., September 18, 2025
	re.compile(r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})"),
	# e.g., Sep 18, 2025
	re.compile(r"([A-Z][a-z]{2}\.?\s+\d{1,2},\s+\d{4})"),
]

BASE_URL = "https://cooper.edu/events"


def extract_first_date(text: str) -> Optional[datetime]:
	if not text:
		return None
	for rx in DATE_REGEXES:
		m = rx.search(text)
		if m:
			try:
				# Normal date format
				parsed = datetime.strptime(m.group(1), "%B %d, %Y") if "," in m.group(1) and len(m.group(1).split()[0]) > 3 else None
				if parsed:
					# Attach New York timezone
					return parsed.replace(tzinfo=NY_TZ)
			except Exception:
				pass
	return None


def is_academic_title(title: str) -> bool:
	t = title.lower()
	return any(k in t for k in ACADEMIC_KEYWORDS)


def scrape_cooper_union_events() -> Dict[str, List[Dict]]:
	resp = requests.get(BASE_URL, timeout=30)
	resp.raise_for_status()
	soup = BeautifulSoup(resp.text, "html.parser")

	events: List[Dict] = []

	# Strategy: Find h3 elements that contain academic event titles
	headers = soup.find_all("h3")
	for h in headers:
		title = (h.get_text() or "").strip()
		if not title:
			continue
		if not is_academic_title(title):
			continue

		# Find a local container to search for date/description
		container = h.parent if h.parent else h
		container_text = " ".join(container.stripped_strings)
		date_dt = extract_first_date(container_text)

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

		# Try to parse a time (and maybe date+time) from the nearby text for a better range
		start_dt: Optional[datetime] = date_dt
		end_dt: Optional[datetime] = None
		try:
			# Examples in text: "December 3, 2025 5:30pm Event Details"
			# First, try full "Month D, YYYY h:mm[am|pm]" pattern
			full_dt_match = re.search(
				r'([A-Z][a-z]+ \d{1,2}, \d{4})\s+(\d{1,2}:\d{2}\s*[ap]m)',
				container_text
			)
			if full_dt_match:
				date_part, time_part = full_dt_match.groups()
				dt = datetime.strptime(f"{date_part} {time_part.replace(' ', '')}", "%B %d, %Y %I:%M%p")
				start_dt = dt.replace(tzinfo=NY_TZ)
			elif date_dt is not None:
				# If we already have a date, try to find just a time like "5:30pm" or "7:00 pm"
				time_match = re.search(r'(\d{1,2}:\d{2}\s*[ap]m)', container_text, flags=re.IGNORECASE)
				if time_match:
					time_part = time_match.group(1)
					dt = datetime.strptime(time_part.replace(" ", ""), "%I:%M%p")
					start_dt = date_dt.replace(hour=dt.hour, minute=dt.minute)

			# Default duration 2 hours if we have a start datetime
			if start_dt is not None:
				end_dt = start_dt + timedelta(hours=2)
		except Exception:
			# Fall back to using date only with default 7–9pm if we have just a date
			if date_dt is not None and start_dt is None:
				start_dt = date_dt.replace(hour=19, minute=0)
				end_dt = start_dt + timedelta(hours=2)

		# If we still have only a date with no time, assign 7–9pm NY time
		if start_dt is None and date_dt is not None:
			start_dt = date_dt.replace(hour=19, minute=0)
			end_dt = start_dt + timedelta(hours=2)

		# Create deterministic ID from title + base url
		uid = hashlib.md5(f"{BASE_URL}::{title}".encode("utf-8")).hexdigest()[:10]

		events.append({
			"id": f"evt_cooper_union_{uid}",
			"name": title,
			"description": description,
			"start_date": standardize_datetime(start_dt) if start_dt else "",
			"end_date": standardize_datetime(end_dt) if end_dt else "",
			"source": "cooper_union",
			"source_group": "cooper_union",
			"metadata": {
				"source_url": BASE_URL,
				"source_name": "Cooper Union",
				"venue": {
					"name": "Cooper Union",
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
		result = scrape_cooper_union_events()
		print(f"Cooper Union events scraped: {len(result.get('events', []))}")
		# Save debug file
		if result.get("events"):
			import json
			with open("cooper_union_events_debug.json", "w", encoding="utf-8") as f:
				json.dump(result, f, ensure_ascii=False, indent=2)
	except Exception as e:
		print(f"Error scraping Cooper Union: {e}")


if __name__ == "__main__":
	main()
