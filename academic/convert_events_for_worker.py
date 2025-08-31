#!/usr/bin/env python3
"""
Convert scraped events to Cloudflare worker format
This script processes all 603 events and formats them for the worker
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any

def clean_html(html_text: str) -> str:
    """Clean HTML tags and entities from text"""
    if not html_text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', html_text)
    
    # Decode HTML entities
    clean_text = clean_text.replace('&amp;', '&')
    clean_text = clean_text.replace('&lt;', '<')
    clean_text = clean_text.replace('&gt;', '>')
    clean_text = clean_text.replace('&quot;', '"')
    clean_text = clean_text.replace('&#39;', "'")
    clean_text = clean_text.replace('&nbsp;', ' ')
    
    # Clean up extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def parse_date(date_str: str) -> str:
    """Parse and format date strings"""
    if not date_str:
        return ""
    
    try:
        # Handle ISO format with timezone
        if 'T' in date_str and '+' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        # Handle other date formats
        elif 'T' in date_str:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%Y-%m-%d')
        else:
            # Assume YYYY-MM-DD format
            return date_str
    except:
        return ""

def convert_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a single event to worker format"""
    
    # Extract venue information
    venue_name = "Location TBD"
    venue_type = "Offline"
    
    if event.get('metadata', {}).get('venue'):
        venue = event['metadata']['venue']
        venue_name = venue.get('name', 'Location TBD').strip()
        venue_type = venue.get('type', 'Offline')
        if venue_type == 'virtual':
            venue_type = 'Virtual'
    
    # Extract source information
    source = event.get('metadata', {}).get('source_name', 'Unknown Institution')
    source_group = event.get('community_id', 'general').replace('com_', '')
    
    # Clean description
    description = clean_html(event.get('description', ''))
    if len(description) > 500:  # Truncate long descriptions
        description = description[:497] + "..."
    
    # Parse dates
    start_date = parse_date(event.get('start_date', ''))
    end_date = parse_date(event.get('end_date', ''))
    
    # Determine if academic
    is_academic = event.get('type', '').lower() == 'academic'
    
    return {
        "id": event.get('id', ''),
        "event_id": event.get('id', ''),
        "name": event.get('name', 'Untitled Event'),
        "type": event.get('type', 'Academic'),
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "source": source.lower().replace(' ', '_').replace('university', ''),
        "source_group": source_group,
        "source_url": event.get('metadata', {}).get('source_url', ''),
        "source_name": source,
        "venue_name": venue_name,
        "venue_type": venue_type,
        "is_academic": is_academic,
        "category": event.get('category', ['General'])
    }

def main():
    """Main conversion function"""
    
    print("🔄 Loading scraped events...")
    
    # Load the scraped events
    with open('scraped_events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_events = data.get('total_events', 0)
    events = data.get('events', [])
    
    print(f"📊 Found {total_events} events to convert")
    
    # Convert all events
    converted_events = []
    for i, event in enumerate(events):
        if i % 100 == 0:
            print(f"🔄 Converting event {i+1}/{total_events}...")
        
        converted_event = convert_event(event)
        converted_events.append(converted_event)
    
    print(f"✅ Converted {len(converted_events)} events")
    
    # Create the worker data file
    worker_data = {
        "generated_at": datetime.now().isoformat(),
        "total_events": len(converted_events),
        "events": converted_events
    }
    
    # Save to worker format
    output_file = 'worker_events.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(worker_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved converted events to {output_file}")
    
    # Generate worker code snippet
    worker_code = f"""// Auto-generated events data - {len(converted_events)} events
// Generated at: {datetime.now().isoformat()}
const academicEvents = {json.dumps(converted_events, indent=2, ensure_ascii=False)};
"""
    
    # Save worker code snippet
    with open('worker_events_code.js', 'w', encoding='utf-8') as f:
        f.write(worker_code)
    
    print(f"📝 Generated worker code snippet in worker_events_code.js")
    
    # Show some stats
    sources = {}
    categories = {}
    for event in converted_events:
        source = event['source']
        sources[source] = sources.get(source, 0) + 1
        
        for cat in event.get('category', []):
            categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📈 Event Statistics:")
    print(f"   Total Events: {len(converted_events)}")
    print(f"   Sources: {len(sources)}")
    print(f"   Categories: {len(categories)}")
    
    print(f"\n🏛️ Top Sources:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {source}: {count} events")
    
    print(f"\n🏷️ Top Categories:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {cat}: {count} events")

if __name__ == "__main__":
    main()
