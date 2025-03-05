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

# Import from our utilities module
from utils.event_utils import (
    load_json_file,
    save_json_file,
    load_events_from_file,
    save_events_to_file,
    convert_event_format,
    extract_locations_and_communities
)

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
        group_categories[group_name] = set()
        
        # Convert each event to the standardized format
        converted_events = []
        for event in events:
            # Add source group to the event
            event['sourceGroup'] = group_name
            
            # Collect categories before conversion
            if 'category' in event:
                categories = event['category']
                if isinstance(categories, list):
                    for category in categories:
                        all_categories.add(category)
                        category_distribution[category] += 1
                        group_categories[group_name].add(category)
                elif isinstance(categories, str):
                    all_categories.add(categories)
                    category_distribution[categories] += 1
                    group_categories[group_name].add(categories)
            
            # Also check for academic-specific categories field
            if 'categories' in event:
                academic_categories = event['categories']
                if isinstance(academic_categories, list):
                    for category in academic_categories:
                        all_categories.add(f"academic_{category}")
                        category_distribution[f"academic_{category}"] += 1
                        group_categories[group_name].add(f"academic_{category}")
            
            # Check for mapped categories
            if 'mappedCategories' in event:
                mapped_categories = event['mappedCategories']
                if isinstance(mapped_categories, list):
                    for category in mapped_categories:
                        all_categories.add(f"mapped_{category}")
                        category_distribution[f"mapped_{category}"] += 1
                        group_categories[group_name].add(f"mapped_{category}")
            
            # Convert the event to the standardized format
            converted_event = convert_event_format(event)
            converted_events.append(converted_event)
        
        all_events.extend(converted_events)
    
    # Convert group_categories sets to lists for JSON serialization
    for group in group_categories:
        group_categories[group] = list(group_categories[group])
    
    # Create metadata about the categories
    category_metadata = {
        "all_categories": list(all_categories),
        "category_distribution": dict(category_distribution),
        "group_categories": group_categories,
        "total_events": len(all_events),
        "total_groups": len(event_files),
        "total_categories": len(all_categories)
    }
    
    # Save category metadata
    save_json_file(category_metadata, OUTPUT_METADATA_PATH)
    logging.info(f"Saved category metadata with {len(all_categories)} unique categories to {OUTPUT_METADATA_PATH}")
    
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