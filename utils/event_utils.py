#!/usr/bin/env python3
"""
Event Utilities Module

Shared functions for processing, converting, and managing events across different sources.
"""

import os
import json
import logging
import hashlib
import re
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('event_utils.log'), logging.StreamHandler()]
)

# Define event categories
class MainCategory(Enum):
    ACADEMIC = "Academic"
    PERFORMANCE = "Performance"
    OTHER = "Other"

# File handling functions
def load_json_file(file_path: str) -> Dict:
    """Load data from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Could not load data from {file_path}: {e}")
        return {}

def save_json_file(data: Dict, file_path: str):
    """Save data to a JSON file"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved data to {file_path}")
    except Exception as e:
        logging.error(f"Error saving data to {file_path}: {e}")

def load_events_from_file(file_path: str) -> List[Dict]:
    """Load events from a JSON file, handling different formats"""
    try:
        data = load_json_file(file_path)
        
        # Handle different formats
        if isinstance(data, dict) and 'events' in data:
            return data['events']
        elif isinstance(data, list):
            return data
        else:
            logging.warning(f"Unexpected format in {file_path}")
            return []
    except Exception as e:
        logging.warning(f"Error loading events from {file_path}: {e}")
        return []

def save_events_to_file(events: List[Dict], file_path: str):
    """Save events to a JSON file in the standard format"""
    save_json_file({'events': events}, file_path)

# Event processing functions
def generate_event_id(source: str, title: str, start_date: str) -> str:
    """Generate a unique ID for an event based on its source, title, and date"""
    # Create a string to hash
    hash_string = f"{source}|{title}|{start_date}"
    
    # Generate a hash
    hash_object = hashlib.md5(hash_string.encode())
    hash_hex = hash_object.hexdigest()
    
    # Return a prefixed ID
    return f"evt_{hash_hex[:16]}"

def clean_venue_name(name: str) -> Tuple[str, str]:
    """Clean venue name and extract address if present"""
    if not name:
        return "", ""
    
    # Split by common separators
    separators = [' - ', ' | ', ' at ', ', ', ' @ ']
    venue_name = name
    address = ""
    
    for separator in separators:
        if separator in name:
            parts = name.split(separator, 1)
            venue_name = parts[0].strip()
            address = parts[1].strip()
            break
    
    # Clean up HTML entities
    venue_name = re.sub(r'&amp;', '&', venue_name)
    address = re.sub(r'&amp;', '&', address)
    
    return venue_name.strip(), address.strip()

def determine_event_categories(event: Dict) -> Tuple[List[str], List[str]]:
    """Determine main categories and event types based on event content"""
    # Extract text for analysis
    title = event.get('title', '')
    description = event.get('description', '')
    
    # Convert to string and handle None values
    title = str(title) if title is not None else ''
    description = str(description) if description is not None else ''
    
    # Combine and convert to lowercase
    combined_text = (title + ' ' + description).lower()
    
    # Initialize categories and types
    main_categories = []
    event_types = []
    
    # First determine event types
    # Academic event types
    if 'lecture' in combined_text:
        event_types.append('Lecture')
        main_categories.append(MainCategory.ACADEMIC.value)
    
    if 'conference' in combined_text:
        event_types.append('Conference')
        main_categories.append(MainCategory.ACADEMIC.value)
    
    if 'research' in combined_text and 'presentation' in combined_text:
        event_types.append('Research Presentation')
        main_categories.append(MainCategory.ACADEMIC.value)
    
    if 'panel' in combined_text or 'discussion' in combined_text:
        event_types.append('Panel Discussion')
        main_categories.append(MainCategory.ACADEMIC.value)
    
    if 'symposium' in combined_text:
        event_types.append('Symposium')
        main_categories.append(MainCategory.ACADEMIC.value)
    
    if 'seminar' in combined_text:
        event_types.append('Seminar')
        main_categories.append(MainCategory.ACADEMIC.value)
        
    if 'workshop' in combined_text:
        event_types.append('Workshop')
        main_categories.append(MainCategory.ACADEMIC.value)
        
    if 'data science' in combined_text or 'machine learning' in combined_text:
        event_types.append('Data Science')
        main_categories.append(MainCategory.ACADEMIC.value)
    
    # Performance event types
    if 'concert' in combined_text or 'music' in combined_text:
        event_types.append('Concert')
        main_categories.append(MainCategory.PERFORMANCE.value)
    
    if 'theater' in combined_text or 'theatre' in combined_text:
        event_types.append('Theater')
        main_categories.append(MainCategory.PERFORMANCE.value)
    
    if 'dance' in combined_text:
        event_types.append('Dance')
        main_categories.append(MainCategory.PERFORMANCE.value)
    
    if 'comedy' in combined_text:
        event_types.append('Comedy')
        main_categories.append(MainCategory.PERFORMANCE.value)
    
    if 'film' in combined_text or 'screening' in combined_text:
        event_types.append('Film Screening')
        main_categories.append(MainCategory.PERFORMANCE.value)
    
    # Check for art exhibition specifically (not just 'art' which is too broad)
    if 'exhibition' in combined_text:
        event_types.append('Art Exhibition')
        main_categories.append(MainCategory.PERFORMANCE.value)
    
    if 'reading' in combined_text or 'literary' in combined_text:
        event_types.append('Literary Reading')
        main_categories.append(MainCategory.PERFORMANCE.value)
    
    # If no specific types were found, check for general keywords
    if not event_types:
        # Check for academic keywords
        academic_keywords = ["academic", "study", "education", "professor", "faculty", "university", "college", "department", "school", "institute", "science", "research"]
        
        # Check for performance keywords
        performance_keywords = ["performance", "gallery", "museum", "show", "play", "opera"]
        
        if any(keyword in combined_text for keyword in academic_keywords):
            main_categories.append(MainCategory.ACADEMIC.value)
        
        if any(keyword in combined_text for keyword in performance_keywords):
            main_categories.append(MainCategory.PERFORMANCE.value)
    
    # If still no categories matched, assign OTHER
    if not main_categories:
        main_categories.append(MainCategory.OTHER.value)
    
    # Remove duplicates while preserving order
    main_categories = list(dict.fromkeys(main_categories))
    event_types = list(dict.fromkeys(event_types))
    
    return main_categories, event_types

def convert_event_format(event: Dict, source_group: str = None) -> Dict:
    """Convert event to standardized format with location and community mapping"""
    # Extract basic event information
    source = event.get('source', 'unknown')
    title = event.get('title', '')
    description = event.get('description', '')
    start_date = event.get('start_date', '')
    end_date = event.get('end_date', '')
    raw_location = event.get('location', '')
    
    # Generate event ID
    event_id = event.get('id') or generate_event_id(source, title, start_date)
    
    # Determine if event is online/virtual
    location = str(raw_location) if raw_location is not None else ''
    description_text = str(description) if description is not None else ''
    
    # Convert to lowercase for checking
    location_lower = location.lower()
    description_lower = description_text.lower()
    
    # Check if event is online/virtual
    is_online = (not location) or any(keyword in location_lower or keyword in description_lower 
                for keyword in ['online', 'virtual', 'zoom', 'webinar', 'livestream'])
    
    # Set venue type and location
    venue_type = "Online" if is_online else "Offline"
    location_id = "loc_virtual" if is_online else f"loc_{source.lower()}_main"
    community_id = f"com_{source.lower()}_general"
    
    # Clean venue name and extract address
    venue_name = str(raw_location) if raw_location is not None else ''
    clean_name, extracted_address = clean_venue_name(venue_name)
    
    # If it's online, override the venue name
    if is_online:
        clean_name = "Online Event"
        extracted_address = ""
    
    # Get or determine categories
    main_categories = event.get('main_categories', [])
    event_types = event.get('event_types', [])
    
    # If categories aren't already set, determine them
    if not main_categories or not event_types:
        determined_categories, determined_types = determine_event_categories(event)
        
        # Use determined values if not already set
        if not main_categories:
            main_categories = determined_categories
        
        if not event_types:
            event_types = determined_types
    
    # Get academic topics if available
    academic_topics = event.get('academic_topics', [])
    
    # Combine all tags for the category field
    all_tags = []
    all_tags.extend(event.get('assigned_tags', []))
    all_tags.extend(main_categories)
    all_tags.extend(event_types)
    all_tags.extend(academic_topics)
    
    # Remove duplicates while preserving order
    all_tags = list(dict.fromkeys(all_tags))
    
    # Create the standardized event
    converted_event = {
        "id": event_id,
        "name": title,
        "type": main_categories[0] if main_categories else "Academic",  # Default to Academic
        "locationId": location_id,
        "communityId": community_id,
        "description": description,
        "startDate": start_date,
        "endDate": end_date,
        "category": all_tags,
        "source": source,
        "sourceGroup": source_group or event.get('sourceGroup', ''),
        "metadata": {
            "sourceUrl": event.get('url', ''),
            "sourceName": f"{source} Events",
            "venue": {
                "name": clean_name,
                "address": extracted_address or event.get('address', ''),
                "type": venue_type
            },
            "additionalInfo": {
                "coordinates": event.get('coordinates', None),
                "accessibility": event.get('accessibility', None),
                "registrationRequired": event.get('registration_required', False),
                "tags": event.get('tags', []),
                "mainCategories": main_categories,
                "eventTypes": event_types,
                "academicTopics": academic_topics
            }
        }
    }
    
    return converted_event

def extract_locations_and_communities(events: List[Dict]) -> Tuple[Dict, Dict]:
    """Extract unique locations and communities from events"""
    locations = {}
    communities = {}
    
    for event in events:
        # Extract location
        location_id = event.get('locationId')
        if location_id and location_id not in locations:
            venue_data = event.get('metadata', {}).get('venue', {})
            locations[location_id] = {
                'id': location_id,
                'name': venue_data.get('name', ''),
                'address': venue_data.get('address', ''),
                'type': venue_data.get('type', 'Offline'),
                'coordinates': event.get('metadata', {}).get('additionalInfo', {}).get('coordinates'),
                'sourceGroup': event.get('sourceGroup', '')
            }
        
        # Extract community
        community_id = event.get('communityId')
        if community_id and community_id not in communities:
            source = event.get('source', '')
            communities[community_id] = {
                'id': community_id,
                'name': source,
                'description': f"Events from {source}",
                'sourceGroup': event.get('sourceGroup', '')
            }
    
    return locations, communities 