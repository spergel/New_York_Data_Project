import json
import os
import re
from typing import List, Dict

def is_academic_event(event: Dict) -> bool:
    """Determine if an event is academic - more inclusive approach"""
    title = event.get('name', event.get('title', '')).lower()
    description = event.get('description', '').lower()
    source = event.get('source', '').lower()
    combined_text = f"{title} {description}"
    
    # Non-academic keywords that indicate this is NOT an academic event
    non_academic_keywords = [
        'blood drive', 'donation', 'fundraiser', 'charity', 'volunteer', 'community service',
        'social', 'party', 'celebration', 'festival', 'concert', 'performance', 'show',
        'exhibition', 'gallery', 'museum', 'tour', 'visit', 'reception', 'dinner',
        'lunch', 'breakfast', 'tea', 'coffee', 'refreshments', 'food', 'drink',
        'shopping', 'market', 'sale', 'pop-up', 'retail', 'store', 'shop',
        'orientation', 'welcome', 'introduction', 'meet and greet', 'networking',
        'career fair', 'job fair', 'recruitment', 'hiring', 'employment',
        'sports', 'athletics', 'fitness', 'exercise', 'workout', 'game', 'match',
        'tournament', 'competition', 'race', 'marathon', 'walk', 'run',
        'sundae soiree', 'ice cream', 'soiree', 'mix and mingle',
        'grand rounds', 'grand round', 'admissions', 'information session', 'webinar',
        'training', 'naloxone', 'study abroad', 'town hall', 'overleaf'
    ]
    
    # Check for non-academic keywords first (exclude these)
    for keyword in non_academic_keywords:
        if keyword in combined_text:
            return False
    
    # Academic event types and keywords
    academic_event_types = [
        'lecture', 'seminar', 'conference', 'symposium', 'workshop', 'colloquium',
        'research presentation', 'thesis defense', 'dissertation defense', 'academic series',
        'lecture series', 'seminar series', 'colloquium series', 'talk', 'presentation',
        'discussion', 'panel', 'roundtable', 'forum', 'research', 'study', 'analysis',
        'mathematics', 'mathematical', 'physics', 'chemistry', 'biology', 'computer science',
        'engineering', 'technology', 'innovation', 'entrepreneurship', 'climate', 'environmental',
        'policy', 'economics', 'philosophy', 'history', 'literature', 'art history',
        'archaeology', 'anthropology', 'sociology', 'psychology', 'neuroscience', 'medicine',
        'health', 'public health', 'urban', 'city', 'architecture', 'design', 'music theory',
        'composition', 'performance studies', 'theater', 'drama', 'film', 'media', 'journalism',
        'law', 'legal', 'business', 'management', 'finance', 'accounting', 'marketing',
        'education', 'pedagogy', 'teaching', 'learning', 'curriculum', 'assessment'
    ]
    
    # Check for academic event types
    for event_type in academic_event_types:
        if event_type in combined_text:
            return True
    
    # Trust certain academic institutions by default (unless they have non-academic keywords)
    trusted_academic_sources = [
        'cims', 'courant', 'cornell_tech', 'hunter', 'pratt', 'simons', 'simons_foundation',
        'barnard', 'cooper_union', 'fordham', 'gallatin', 'isaw', 'jtsa', 'new_school',
        'nyu', 'nyu_engineering', 'nyu_cims', 'nyu_education', 'nyu_law', 'nyu_medicine', 'nyu_stern',
        'columbia', 'columbia_classics', 'columbia_general', 'columbia_history', 'columbia_law', 
        'columbia_math', 'columbia_religion', 'columbia_social_difference'
    ]
    
    # If it's from a trusted academic source and doesn't have non-academic keywords, include it
    if source in trusted_academic_sources:
        return True
    
    return False

def clean_event_data(event: Dict) -> Dict:
    """Clean and standardize event data"""
    # Get the correct title
    title = event.get('name', event.get('title', ''))
    
    # Clean HTML from description
    description = event.get('description', '')
    if description:
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        # Decode HTML entities
        description = description.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
        # Clean up extra whitespace
        description = re.sub(r'\s+', ' ', description).strip()
    
    # Get venue information from metadata
    venue_name = ''
    venue_address = ''
    is_online = False
    
    metadata = event.get('metadata', {})
    venue_info = metadata.get('venue', {})
    
    if venue_info:
        venue_name = venue_info.get('name', '')
        venue_address = venue_info.get('address', '')
        
        # Check if it's actually online
        online_keywords = ['online', 'virtual', 'zoom', 'webinar', 'livestream', 'remote']
        if any(keyword in str(venue_name).lower() for keyword in online_keywords):
            is_online = True
            venue_name = 'Online Event'
    
    # Create cleaned event
    cleaned_event = {
        "id": event.get('id', event.get('event_id', '')),
        "name": title,
        "type": "Academic",
        "locationId": "loc_virtual" if is_online else f"loc_{event.get('source', 'unknown')}_main",
        "communityId": f"com_{event.get('source', 'unknown')}_general",
        "description": description,
        "startDate": event.get('start_date', ''),
        "endDate": event.get('end_date', ''),
        "category": ["Academic"],
        "source": event.get('source', 'unknown'),
        "sourceGroup": "academic",
        "metadata": {
            "sourceUrl": metadata.get('source_url', ''),
            "sourceName": f"{event.get('source', 'unknown')} Events",
            "venue": {
                "name": venue_name,
                "address": venue_address,
                "type": "Online" if is_online else "Offline"
            },
            "additionalInfo": {
                "coordinates": None,
                "accessibility": None,
                "registrationRequired": False,
                "tags": [],
                "mainCategories": ["Academic"],
                "eventTypes": [],
                "academicTopics": []
            }
        }
    }
    
    return cleaned_event

def filter_academic_events(input_file: str, output_file: str):
    """Filter events to only include academic ones and clean the data"""
    print(f"Loading events from {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    print(f"Found {len(events)} total events")
    
    # Filter for academic events
    academic_events = []
    for event in events:
        if is_academic_event(event):
            cleaned_event = clean_event_data(event)
            academic_events.append(cleaned_event)
    
    print(f"Filtered to {len(academic_events)} academic events")
    
    # Save filtered events
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'events': academic_events}, f, ensure_ascii=False, indent=2)
    
    print(f"Saved academic events to {output_file}")
    
    # Print some examples
    print("\nExample academic events:")
    for i, event in enumerate(academic_events[:5]):
        print(f"{i+1}. {event['name']} ({event['source']})")
        print(f"   Date: {event['startDate']}")
        print(f"   Venue: {event['metadata']['venue']['name']}")
        print()

if __name__ == "__main__":
    # Filter the raw events instead of converted events
    input_file = "events_test/all_events.json"
    output_file = "events_test/academic_events_filtered.json"
    
    if os.path.exists(input_file):
        filter_academic_events(input_file, output_file)
    else:
        print(f"Input file {input_file} not found!")
