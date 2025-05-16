#!/usr/bin/env python3
"""
Combine JSON Files

This script searches for and combines JSON files (events, locations, communities)
from different group directories into unified datasets.
"""

import os
import logging
import glob
from typing import List, Dict, Set, Counter
from pathlib import Path
from collections import Counter
from datetime import datetime

# Import from our utilities module
from utils.event_utils import (
    load_json_file,
    save_json_file,
    load_events_from_file,
    save_events_to_file,
    convert_event_format,
    extract_locations_and_communities
)

# Import from general models
from general.models import EventCategory, EventStatus, Price, Venue, Organizer, EventMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('combine_json.log'), logging.StreamHandler()]
)

# Output directory and file paths
OUTPUT_DIR = "combined"
OUTPUT_EVENTS_PATH = os.path.join(OUTPUT_DIR, "combined_events.json")
OUTPUT_LOCATIONS_PATH = os.path.join(OUTPUT_DIR, "combined_locations.json")
OUTPUT_COMMUNITIES_PATH = os.path.join(OUTPUT_DIR, "combined_communities.json")
OUTPUT_METADATA_PATH = os.path.join(OUTPUT_DIR, "combined_metadata.json")

def find_json_files(pattern: str) -> List[str]:
    """Find all JSON files matching the given pattern"""
    files = glob.glob(pattern, recursive=True)
    logging.info(f"Found {len(files)} files matching pattern: {pattern}")
    return files

def extract_group_name(file_path: str) -> str:
    """Extract the group name from the file path"""
    # Extract the first directory name from the path
    parts = Path(file_path).parts
    if len(parts) > 0:
        return parts[0]
    return "unknown"

def standardize_event_fields(event: Dict, source_group: str) -> Dict:
    """
    Standardize event fields to a common format while preserving essential data.
    Ensures consistent field names and removes extraneous fields.
    """
    # Create a new standardized event with only the fields we want
    standardized = {}
    
    # Essential fields - preserve and standardize names
    standardized['id'] = event.get('id', '')
    
    # Name field - could be 'name', 'title', or others
    standardized['name'] = event.get('name', event.get('title', ''))
    
    # Type field
    standardized['type'] = event.get('type', '')
    
    # Description field
    standardized['description'] = event.get('description', '')
    
    # Dates - standardize to start_date and end_date
    standardized['start_date'] = event.get('start_date', event.get('startDate', event.get('start_time', '')))
    standardized['end_date'] = event.get('end_date', event.get('endDate', event.get('end_time', '')))
    
    # Location and community - standardize field names
    standardized['location_id'] = event.get('location_id', event.get('locationId', ''))
    standardized['community_id'] = event.get('community_id', event.get('communityId', ''))
    
    # Categories - map to unified EventCategory enum
    categories = set()
    
    # Process original categories
    if 'category' in event:
        orig_cats = event['category']
        if isinstance(orig_cats, list):
            for cat in orig_cats:
                # Try to map the category to our enum
                cat_str = str(cat).upper()
                try:
                    # Try direct mapping
                    categories.add(EventCategory[cat_str])
                except KeyError:
                    # Try to find a matching category
                    for enum_cat in EventCategory:
                        if cat_str in enum_cat.value or cat_str in enum_cat.name:
                            categories.add(enum_cat)
                            break
    
    # Process academic categories
    if 'categories' in event:
        academic_cats = event['categories']
        if isinstance(academic_cats, list):
            for cat in academic_cats:
                if isinstance(cat, dict) and 'id' in cat:
                    cat_id = cat['id'].upper()
                    try:
                        categories.add(EventCategory[cat_id])
                    except KeyError:
                        pass
                elif isinstance(cat, str):
                    cat_str = cat.upper()
                    try:
                        categories.add(EventCategory[cat_str])
                    except KeyError:
                        pass
    
    # Process tech categories
    if 'tech_categories' in event:
        tech_cats = event['tech_categories']
        if isinstance(tech_cats, list):
            for cat in tech_cats:
                if isinstance(cat, dict) and 'id' in cat:
                    cat_id = f"TECH_{cat['id'].upper()}"
                    try:
                        categories.add(EventCategory[cat_id])
                    except KeyError:
                        pass
    
    # Process exercise categories
    if 'exercise_categories' in event:
        exercise_cats = event['exercise_categories']
        if isinstance(exercise_cats, list):
            for cat in exercise_cats:
                if isinstance(cat, str):
                    cat_str = cat.upper()
                    try:
                        categories.add(EventCategory[cat_str])
                    except KeyError:
                        pass
    
    # If no categories were mapped, add OTHER
    if not categories:
        categories.add(EventCategory.OTHER)
    
    standardized['category'] = list(categories)
    
    # Price information
    if 'price' in event:
        standardized['price'] = event['price']
    else:
        # Create default price object
        standardized['price'] = {
            'amount': 0.0,
            'type': 'free',
            'details': None
        }
    
    # Status
    if 'status' in event:
        standardized['status'] = event.get('status', 'scheduled')
    
    # Tags
    if 'tags' in event:
        standardized['tags'] = event['tags']
    
    # Registration info
    if 'registration_required' in event:
        standardized['registration_required'] = event['registration_required']
    
    # Image URL
    if 'image_url' in event:
        standardized['image_url'] = event['image_url']
    
    # Metadata - preserve but standardize structure
    standardized['metadata'] = {
        'source_url': '',
        'source_name': source_group
    }
    
    if 'metadata' in event:
        standardized['metadata'].update(event['metadata'])
    else:
        # Try to construct metadata from individual fields
        if 'venue' in event:
            standardized['metadata']['venue'] = event['venue']
        if 'organizer' in event:
            standardized['metadata']['organizer'] = event['organizer']
        if 'source_url' in event:
            standardized['metadata']['source_url'] = event['source_url']
        if 'source_name' in event:
            standardized['metadata']['source_name'] = event['source_name']
    
    # Add source group
    standardized['source_group'] = source_group
    
    return standardized

def combine_events():
    """Find and combine event JSON files"""
    # Find all event JSON files (specifically named events.json)
    event_files = find_json_files("*/data/events.json")
    
    all_events = []
    all_categories = set()
    category_distribution = Counter()
    group_categories = {}
    
    for file_path in event_files:
        group_name = extract_group_name(file_path)
        events = load_events_from_file(file_path)
        
        logging.info(f"Loaded {len(events)} events from {file_path}")
        
        # Track categories by group
        group_categories[group_name] = Counter()
        
        # Process each event
        for event in events:
            # Check if event matches our criteria
            is_networking = False
            
            # Check categories for networking_social
            if 'category' in event:
                categories = event.get('category', [])
                if not isinstance(categories, list):
                    categories = [categories]
                
                # Check each category - it might be a dict with an id field
                for cat in categories:
                    if isinstance(cat, dict) and cat.get('id') == 'networking_social':
                        is_networking = True
                        break
                    elif str(cat) == 'networking_social':
                        is_networking = True
                        break
            
            # Only process events that match our criteria
            if is_networking:
                # Add source group to the event
                event['source_group'] = group_name
                
                # Track category statistics
                if 'category' in event:
                    for cat in categories:
                        # Handle both dict and string categories
                        if isinstance(cat, dict):
                            cat_str = cat.get('id', '').lower()
                        else:
                            cat_str = str(cat).lower()
                        all_categories.add(cat_str)
                        category_distribution[cat_str] += 1
                        group_categories[group_name][cat_str] += 1
                
                all_events.append(event)
    
    # Create metadata about the categories
    category_metadata = {
        "statistics": {
            "total_events": len(all_events),
            "total_categories": len(all_categories),
            "category_distribution": {
                cat: {
                    'count': count,
                    'percentage': round(count / len(all_events) * 100, 2)
                }
                for cat, count in category_distribution.most_common()
            },
            "by_group": {
                group: {
                    cat: {
                        'count': count,
                        'percentage': round(count / sum(counts.values()) * 100, 2)
                    }
                    for cat, count in counts.most_common()
                }
                for group, counts in group_categories.items()
            }
        }
    }
    
    # Save category metadata
    save_json_file(category_metadata, OUTPUT_METADATA_PATH)
    logging.info(f"Saved category statistics with {len(all_categories)} unique categories to {OUTPUT_METADATA_PATH}")
    
    # Save combined events
    save_events_to_file(all_events, OUTPUT_EVENTS_PATH)
    logging.info(f"Combined {len(all_events)} events from {len(event_files)} files")
    
    return all_events

def combine_locations():
    """Find and combine location JSON files"""
    # Find all location JSON files
    location_files = find_json_files("*/data/locations.json")
    
    all_locations = {}
    
    for file_path in location_files:
        group_name = extract_group_name(file_path)
        data = load_json_file(file_path)
        
        # Extract locations from the file
        locations = data.get('locations', [])
        logging.info(f"Loaded {len(locations)} locations from {file_path}")
        
        # Add each location to the combined dictionary, using ID as key to avoid duplicates
        for location in locations:
            if 'id' in location:
                location['sourceGroup'] = group_name
                all_locations[location['id']] = location
    
    return all_locations

def combine_communities():
    """Find and combine community JSON files"""
    # Find all community JSON files
    community_files = find_json_files("*/data/communities.json")
    
    all_communities = {}
    
    for file_path in community_files:
        group_name = extract_group_name(file_path)
        data = load_json_file(file_path)
        
        # Extract communities from the file
        communities = data.get('communities', [])
        logging.info(f"Loaded {len(communities)} communities from {file_path}")
        
        # Add each community to the combined dictionary, using ID as key to avoid duplicates
        for community in communities:
            if 'id' in community:
                community['sourceGroup'] = group_name
                all_communities[community['id']] = community
    
    return all_communities

def main():
    """Main function to combine JSON files"""
    logging.info("Starting JSON file combination process...")
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Combine events
    all_events = combine_events()
    
    # Combine locations from location files
    all_locations = combine_locations()
    logging.info(f"Combined {len(all_locations)} locations from location files")
    
    # Combine communities from community files
    all_communities = combine_communities()
    logging.info(f"Combined {len(all_communities)} communities from community files")
    
    # Extract additional locations and communities from events
    extracted_locations, extracted_communities = extract_locations_and_communities(all_events)
    
    # Merge extracted locations with loaded locations
    for loc_id, location in extracted_locations.items():
        if loc_id not in all_locations:
            all_locations[loc_id] = location
    
    # Merge extracted communities with loaded communities
    for com_id, community in extracted_communities.items():
        if com_id not in all_communities:
            all_communities[com_id] = community
    
    # Save combined locations and communities
    save_json_file({'locations': list(all_locations.values())}, OUTPUT_LOCATIONS_PATH)
    logging.info(f"Saved {len(all_locations)} locations to {OUTPUT_LOCATIONS_PATH}")
    
    save_json_file({'communities': list(all_communities.values())}, OUTPUT_COMMUNITIES_PATH)
    logging.info(f"Saved {len(all_communities)} communities to {OUTPUT_COMMUNITIES_PATH}")
    
    logging.info("JSON file combination process completed successfully")

if __name__ == '__main__':
    main() 