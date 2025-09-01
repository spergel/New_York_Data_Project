#!/usr/bin/env python3
"""
Convert scraped events to Cloudflare Worker format
"""

import json
import re
from datetime import datetime
from typing import Dict, Any

def clean_venue_name(venue_name: str) -> str:
    """Clean and standardize venue names"""
    if not venue_name:
        return "Location TBD"
    
    # Remove common artifacts
    venue = venue_name.strip()
    venue = re.sub(r'\\,', ',', venue)  # Fix escaped commas
    venue = re.sub(r'\\', '', venue)    # Remove backslashes
    
    # Truncate if too long
    if len(venue) > 200:
        venue = venue[:197] + "..."
    
    return venue

def convert_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a scraped event to worker format"""
    
    # Extract basic fields
    event_id = event.get('id', '')
    name = event.get('name', 'Untitled Event')
    description = event.get('description', '')
    start_date = event.get('start_date', '')
    end_date = event.get('end_date', start_date)
    source = event.get('source', 'unknown')
    source_group = event.get('source_group', source)
    
    # Extract metadata
    metadata = event.get('metadata', {})
    source_url = metadata.get('source_url', '')
    source_name = metadata.get('source_name', 'Unknown Institution')
    venue_info = metadata.get('venue', {})
    venue_name = clean_venue_name(venue_info.get('name', ''))
    venue_type = venue_info.get('type', 'Offline')
    
    # Clean description
    if description:
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        # Remove extra whitespace
        description = re.sub(r'\s+', ' ', description).strip()
        # Truncate if too long
        if len(description) > 1000:
            description = description[:997] + "..."
    
    # Clean name
    if len(name) > 200:
        name = name[:197] + "..."
    
    # Format source name
    source_name_clean = source_name.lower().replace(' ', '_').replace('university', '').replace('_', '')
    
    # Create worker event
    worker_event = {
        "id": event_id,
        "name": name,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "source": source,
        "source_group": source_group,
        "source_name": source_name_clean,
        "source_url": source_url,
        "venue": {
            "name": venue_name,
            "type": venue_type
        },
        "metadata": {
            "scraped_at": datetime.now().isoformat(),
            "original_source": source_name
        }
    }
    
    return worker_event

def main():
    """Convert all events from scraped_events.json to worker format"""
    try:
        # Load scraped events
        with open('scraped_events.json', 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        events = scraped_data.get('events', [])
        print(f"🔄 Converting {len(events)} events for worker...")
        
        # Convert events
        converted_events = []
        for i, event in enumerate(events):
            if i % 100 == 0:
                print(f"🔄 Converting event {i+1}/{len(events)}...")
            
            converted_event = convert_event(event)
            converted_events.append(converted_event)
        
        # Save worker events
        worker_data = {
            "generated_at": datetime.now().isoformat(),
            "total_events": len(converted_events),
            "events": converted_events
        }
        
        with open('worker_events.json', 'w', encoding='utf-8') as f:
            json.dump(worker_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Converted {len(converted_events)} events for worker")
        print(f"💾 Saved worker events to worker_events.json")
        
    except FileNotFoundError:
        print("❌ scraped_events.json not found. Run scrapers first.")
    except Exception as e:
        print(f"❌ Error converting events: {e}")

if __name__ == "__main__":
    main()
