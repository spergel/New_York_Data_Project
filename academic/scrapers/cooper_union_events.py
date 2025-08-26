import requests
import re
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional

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
					return parsed.date().isoformat()
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
			"id": f"evt_cooper_union_{uid}",
			"name": title,
			"description": description,
			"start_date": date_iso or "",
			"end_date": "",
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
			with open("events_test/cooper_union_events.json", "w", encoding="utf-8") as f:
				json.dump(result, f, ensure_ascii=False, indent=2)
	except Exception as e:
		print(f"Error scraping Cooper Union: {e}")


if __name__ == "__main__":
	main()
