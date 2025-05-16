#!/usr/bin/env python3
import json
import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
log_dir = "academic/logs"
log_file = os.path.join(log_dir, f"combine_events_{datetime.now().strftime('%Y%m%d')}.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('combine_events')

def load_json_file(file_path: str) -> Optional[Dict]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json_file(data: Any, file_path: str) -> bool:
    """Save data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")
        return False

def combine_events(institution_events_path: Optional[str] = None, 
                  tech_events_path: Optional[str] = None,
                  nymas_events_path: Optional[str] = None,
                  output_path: str = None) -> List[Dict]:
    """
    Combine events from multiple sources.
    
    Args:
        institution_events_path: Path to the institution events JSON file
        tech_events_path: Path to the tech events JSON file
        nymas_events_path: Path to the NYMAS events JSON file
        output_path: Path where to save the combined events
    
    Returns:
        List of combined events
    """
    all_event_data = []
    
    # Load data from each source if provided
    if institution_events_path and os.path.exists(institution_events_path):
        institution_data = load_json_file(institution_events_path)
        if institution_data:
            all_event_data.append(("institution", institution_data))
            logging.info(f"Loaded institution events from {institution_events_path}")
        else:
            logging.warning(f"Failed to load institution events from {institution_events_path}")
    
    if tech_events_path and os.path.exists(tech_events_path):
        tech_data = load_json_file(tech_events_path)
        if tech_data:
            all_event_data.append(("tech", tech_data))
            logging.info(f"Loaded tech events from {tech_events_path}")
        else:
            logging.warning(f"Failed to load tech events from {tech_events_path}")
    
    if nymas_events_path and os.path.exists(nymas_events_path):
        nymas_data = load_json_file(nymas_events_path)
        if nymas_data:
            all_event_data.append(("nymas", nymas_data))
            logging.info(f"Loaded NYMAS events from {nymas_events_path}")
        else:
            logging.warning(f"Failed to load NYMAS events from {nymas_events_path}")
    
    if not all_event_data:
        logging.error("No event data was loaded from any source")
        return []
    
    # Create event ID lookup to avoid duplicates
    event_ids = set()
    combined_events = []
    
    # Process each data source
    for source_name, source_data in all_event_data:
        source_events = source_data.get("events", [])
        logging.info(f"Processing {len(source_events)} events from {source_name} source")
        
        # Add events from this source
        for event in source_events:
            event_id = event.get("id", "")
            if event_id and event_id not in event_ids:
                event_ids.add(event_id)
                combined_events.append(event)
            elif not event_id:
                # If no ID, use a combination of name and start date
                pseudo_id = f"{event.get('name', '')}-{event.get('startDate', '')}"
                if pseudo_id not in event_ids:
                    event_ids.add(pseudo_id)
                    combined_events.append(event)
                else:
                    logging.debug(f"Skipping duplicate event: {pseudo_id}")
    
    logging.info(f"Combined events: {len(combined_events)}")
    
    # Save combined events if output path is provided
    if output_path and combined_events:
        save_json_file({"events": combined_events}, output_path)
        logging.info(f"Saved {len(combined_events)} combined events to {output_path}")
    
    return combined_events

def main():
    """Main entry point."""
    try:
        # Set up command line arguments
        parser = argparse.ArgumentParser(description='Combine events from different sources')
        parser.add_argument('--institution-events', 
                           help='Path to institution events file')
        parser.add_argument('--tech-events', 
                           help='Path to tech events file')
        parser.add_argument('--nymas-events',
                           help='Path to NYMAS events file')
        parser.add_argument('--output', '-o', default='academic/data/combined_events.json', 
                           help='Output file path')
        parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
        args = parser.parse_args()
        
        # Configure more verbose logging if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Log data sources
        if args.institution_events:
            logging.info(f"Using institution events from: {args.institution_events}")
        if args.tech_events:
            logging.info(f"Using tech events from: {args.tech_events}")
        if args.nymas_events:
            logging.info(f"Using NYMAS events from: {args.nymas_events}")
        
        logging.info(f"Output will be saved to: {args.output}")
        
        # Check if at least one input source is provided
        if not any([args.institution_events, args.tech_events, args.nymas_events]):
            error_msg = "Error: At least one event source must be provided."
            logging.error(error_msg)
            print(error_msg)
            return 1
        
        # Combine events
        combined_events = combine_events(
            args.institution_events,
            args.tech_events,
            args.nymas_events,
            args.output
        )
        
        logging.info(f"Successfully combined {len(combined_events)} events")
        
        return 0
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 