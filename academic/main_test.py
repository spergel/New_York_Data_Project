import json
import os
from datetime import datetime
from typing import List, Dict
import re
import hashlib
import importlib
import logging
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from utils
from utils.event_utils import (
    generate_event_id, 
    clean_venue_name, 
    convert_event_format,
    save_events_to_file,
    load_events_from_file
)

# Import functions to fetch events from all sources
from scrapers.columbia_general_events import scrape_columbia_events
# from scrapers.cuny_general_events import scrape_cuny_events  # File doesn't exist
# from scrapers.sof_heyman_events import scrape_sofheyman_events
from scrapers.new_school_events import scrape_new_school_events
from scrapers.isaw_events import scrape_isaw_events
from scrapers.nyu_engineering import scrape_nyu_engineering_events
from scrapers.cornell_tech_events import scrape_cornell_tech_events
from scrapers.barnard_events import scrape_barnard_events
from scrapers.gallatin_events import scrape_gallatin_events
from scrapers.jtsa_events import scrape_jtsa_events
from scrapers.juilliard_events import scrape_juilliard_events
from scrapers.miller_events import scrape_miller_theatre_events
from scrapers.nyu_cims_events import scrape_cims_events
from scrapers.nyu_general_events import scrape_nyu_general_events
from scrapers.simons_foundation_events import scrape_simons_events

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('academic_scraping_test.log'), logging.StreamHandler()]
)

def run_all_scrapers(output_dir: str = "events_test") -> Dict[str, List[dict]]:
    """Run all scrapers and save results to individual files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Dictionary to store results from each scraper
    all_results = {}
    
    # Track statistics
    successful_scrapers = 0
    failed_scrapers = 0
    empty_results = 0
    
    # Get all scraper modules from the scrapers directory
    scrapers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapers")
    scraper_files = [f for f in os.listdir(scrapers_dir) if f.endswith('.py') and not f.startswith('__')]
    
    for scraper_file in scraper_files:
        # Get module name without .py extension
        module_name = scraper_file[:-3]
        
        # Skip any test files
        if module_name.startswith('test_'):
            continue
            
        try:
            # Import the module dynamically
            module_path = f"scrapers.{module_name}"
            scraper_module = importlib.import_module(module_path)
            
            # Find the scrape function in the module
            scrape_functions = [f for f in dir(scraper_module) if f.startswith('scrape_') and callable(getattr(scraper_module, f))]
            
            if not scrape_functions:
                logging.warning(f"No scrape function found in {module_name}")
                continue
                
            # Use the first scrape function found
            scrape_function_name = scrape_functions[0]
            scrape_function = getattr(scraper_module, scrape_function_name)
            
            # Extract source name from function name
            source_name = scrape_function_name.replace('scrape_', '').replace('_events', '')
            
            # Run the scraper
            print(f"Running {source_name} scraper...")
            scraper_result = scrape_function()
            
            # Handle different return types
            if isinstance(scraper_result, dict) and 'events' in scraper_result:
                events = scraper_result['events']
            elif isinstance(scraper_result, list):
                events = scraper_result
            elif isinstance(scraper_result, str):
                # Some scrapers might return a string (e.g., JSON string)
                try:
                    parsed_result = json.loads(scraper_result)
                    if isinstance(parsed_result, dict) and 'events' in parsed_result:
                        events = parsed_result['events']
                    elif isinstance(parsed_result, list):
                        events = parsed_result
                    else:
                        events = []
                except json.JSONDecodeError:
                    events = []
            else:
                events = []
            
            # Convert events to the expected format
            standardized_events = []
            for event in events:
                # Create a copy of the event to avoid modifying the original
                if isinstance(event, dict):
                    standardized_event = event.copy()
                else:
                    # Skip non-dict events
                    continue
                
                # Add source to each event
                if 'source' not in standardized_event:
                    standardized_event['source'] = source_name
                
                # Standardize field names
                field_mappings = {
                    'id': 'event_id',
                    'location_id': 'locationId',
                    'community_id': 'communityId'
                }
                
                for old_field, new_field in field_mappings.items():
                    if old_field in standardized_event and new_field not in standardized_event:
                        standardized_event[new_field] = standardized_event[old_field]
                
                # Generate event_id if not present
                if 'event_id' not in standardized_event and 'id' not in standardized_event:
                    title = standardized_event.get('title', '')
                    start_date = standardized_event.get('start_date', '')
                    standardized_event['event_id'] = generate_event_id(source_name, title, start_date)
                
                standardized_events.append(standardized_event)
            
            # Save results to file
            if standardized_events:
                file_path = os.path.join(output_dir, f"{source_name}_events.json")
                save_events_to_file(standardized_events, file_path)
                print(f"Successfully scraped {len(standardized_events)} events from {source_name}")
                successful_scrapers += 1
            else:
                print(f"No events found from {source_name}")
                empty_results += 1
            
            # Store results
            all_results[source_name] = standardized_events
            
        except Exception as e:
            print(f"Error running {module_name} scraper: {e}")
            failed_scrapers += 1
    
    # Print summary
    total_events = sum(len(events) for events in all_results.values())
    print(f"\nScraping complete. Results saved to {output_dir}/")
    print(f"Total events scraped: {total_events}")
    print(f"Successful scrapers: {successful_scrapers}")
    print(f"Failed scrapers: {failed_scrapers}")
    print(f"Empty results: {empty_results}")
    
    return all_results

def main():
    # Create output directory
    os.makedirs("events_test", exist_ok=True)
    
    # Run all scrapers
    print("Running all scrapers (TEST MODE - NO LLM TAGGING)...")
    all_results = run_all_scrapers()
    
    # Flatten the results
    all_events = [event for events in all_results.values() for event in events]
    
    # Skip LLM tagging - just add basic tags based on source
    print(f"\nSkipping LLM tagging for {len(all_events)} events...")
    print("Events will be saved without advanced tagging.")
    
    # Convert events to standardized format
    print("\nConverting events to standardized format...")
    converted_events = []
    for event in all_events:
        try:
            # Add sourceGroup field for tracking
            event['sourceGroup'] = 'academic'
            converted_event = convert_event_format(event)
            converted_events.append(converted_event)
        except Exception as e:
            print(f"Error converting event {event.get('event_id', 'unknown')}: {e}")
    
    # Save final results
    events_file = os.path.join("events_test", "all_events.json")
    converted_events_file = os.path.join("events_test", "converted_events.json")
    
    save_events_to_file(all_events, events_file)
    save_events_to_file(converted_events, converted_events_file)
    
    print(f"Saved {len(all_events)} events to {events_file}")
    print(f"Saved {len(converted_events)} converted events to {converted_events_file}")
    
    # Skip advanced categorization for now
    print("\nSkipping advanced categorization system for testing...")
    print("Test complete! Check the events_test/ directory for results.")

if __name__ == "__main__":
    main()
