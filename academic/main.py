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

from llm_generate_tags import assign_event_tags, load_model, AcademicType, PerformanceType, AcademicTopic

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
    handlers=[logging.FileHandler('academic_scraping.log'), logging.StreamHandler()]
)

def run_all_scrapers(output_dir: str = "events") -> Dict[str, List[dict]]:
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
    os.makedirs("events", exist_ok=True)
    
    # Run all scrapers
    print("Running all scrapers...")
    all_results = run_all_scrapers()
    
    # Flatten the results
    all_events = [event for events in all_results.values() for event in events]
    
    # Assign tags to events that don't have them
    events_to_tag = [event for event in all_events if 'assigned_tags' not in event]
    if events_to_tag:
        print(f"\nAssigning tags to {len(events_to_tag)} events...")
        
        # Load model
        model = load_model()
        
        # Create a comprehensive list of all possible tags
        all_tags = [
            *[cat.value for cat in AcademicType],
            *[cat.value for cat in PerformanceType],
            *[topic.value for cat in AcademicTopic]
        ]
        # Add some more general tags
        all_tags.extend(["Science", "Technology", "Arts", "Humanities", "Social Sciences", "Engineering", "Business", "Law", "Medicine", "Education"])
        all_tags = list(set(all_tags))  # Remove duplicates
        
        # Process events in batches
        batch_size = 50  # Adjust batch size as needed
        tagged_events = []
        
        for i in range(0, len(events_to_tag), batch_size):
            batch = events_to_tag[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(events_to_tag) + batch_size - 1)//batch_size}...")
            batch_tagged = assign_event_tags(model, batch, all_tags)
            tagged_events.extend(batch_tagged)
        
        # Update events with new tags
        for event in tagged_events:
            event_id = event['event_id']
            matching_events = [e for e in all_events if e.get('event_id') == event_id]
            for matching_event in matching_events:
                matching_event['assigned_tags'] = event['assigned_tags']
                matching_event['main_categories'] = event['main_categories']
                matching_event['event_types'] = event['event_types']
                matching_event['academic_topics'] = event['academic_topics']
                matching_event['tag_note'] = event['tag_note']
    
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
    events_file = os.path.join("events", "all_events.json")
    converted_events_file = os.path.join("events", "converted_events.json")
    
    save_events_to_file(all_events, events_file)
    save_events_to_file(converted_events, converted_events_file)
    
    print(f"Saved {len(all_events)} events to {events_file}")
    print(f"Saved {len(converted_events)} converted events to {converted_events_file}")
    
    # Run the advanced categorization system
    try:
        print("\nRunning advanced categorization system...")
        import categorize_events
        categorize_events.main()
        print("Advanced categorization complete!")
        
        # Check if categorized events file exists
        categorized_file = os.path.join("events", "categorized_events.json")
        if os.path.exists(categorized_file):
            print(f"Categorized events saved to {categorized_file}")
            
            # Optionally merge the categorized data back into the main events
            try:
                from utils.event_utils import load_json_file
                categorized_events = load_json_file(categorized_file)
                
                # Create a mapping of event_id to detailed categories
                event_categories = {}
                for event in categorized_events:
                    if 'event_id' in event and 'detailed_categories' in event:
                        event_categories[event['event_id']] = {
                            'detailed_categories': event['detailed_categories'],
                            'main_categories': event.get('main_categories', [])
                        }
                
                # Update the original events with the detailed categories
                updated_count = 0
                for event in all_events:
                    event_id = event.get('event_id')
                    if event_id in event_categories:
                        event['detailed_categories'] = event_categories[event_id]['detailed_categories']
                        event['main_categories'] = event_categories[event_id]['main_categories']
                        updated_count += 1
                
                # Save the updated events
                save_events_to_file(all_events, events_file)
                print(f"Updated {updated_count} events with detailed categories")
            except Exception as e:
                print(f"Error merging categorized data: {e}")
    except Exception as e:
        print(f"Error running advanced categorization: {e}")

if __name__ == "__main__":
    main()
