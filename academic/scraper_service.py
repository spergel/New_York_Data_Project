import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict
import importlib

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Event
from utils.event_utils import convert_event_format
from filter_academic_events import is_academic_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_all_scrapers() -> Dict[str, List[dict]]:
    """Run all scrapers and return results."""
    all_results = {}
    
    # Get all scraper modules from the scrapers directory
    scrapers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapers")
    scraper_files = [f for f in os.listdir(scrapers_dir) if f.endswith('.py') and not f.startswith('__')]
    
    for scraper_file in scraper_files:
        module_name = scraper_file[:-3]
        
        # Skip test files
        if module_name.startswith('test_'):
            continue
            
        try:
            # Import the module dynamically
            module_path = f"scrapers.{module_name}"
            scraper_module = importlib.import_module(module_path)
            
            # Find the scrape function
            scrape_functions = [f for f in dir(scraper_module) if f.startswith('scrape_') and callable(getattr(scraper_module, f))]
            
            if not scrape_functions:
                logging.warning(f"No scrape function found in {module_name}")
                continue
                
            scrape_function_name = scrape_functions[0]
            scrape_function = getattr(scraper_module, scrape_function_name)
            
            # Extract source name
            source_name = scrape_function_name.replace('scrape_', '').replace('_events', '')
            
            # Run the scraper
            logging.info(f"Running {source_name} scraper...")
            scraper_result = scrape_function()
            
            # Handle different return types
            if isinstance(scraper_result, dict) and 'events' in scraper_result:
                events = scraper_result['events']
            elif isinstance(scraper_result, list):
                events = scraper_result
            else:
                events = []
            
            # Standardize events
            standardized_events = []
            for event in events:
                if isinstance(event, dict):
                    standardized_event = event.copy()
                    if 'source' not in standardized_event:
                        standardized_event['source'] = source_name
                    standardized_events.append(standardized_event)
            
            all_results[source_name] = standardized_events
            logging.info(f"Successfully scraped {len(standardized_events)} events from {source_name}")
            
        except Exception as e:
            logging.error(f"Error running {module_name} scraper: {e}")
    
    return all_results

def save_events_to_database(events: List[dict]):
    """Save events to the database."""
    db = SessionLocal()
    try:
        # Clear existing events
        db.query(Event).delete()
        db.commit()
        
        # Insert new events
        for event_data in events:
            # Convert to database format
            db_event = Event(
                event_id=event_data.get('id', ''),
                name=event_data.get('name', ''),
                description=event_data.get('description', ''),
                start_date=event_data.get('start_date', ''),
                end_date=event_data.get('end_date', ''),
                source=event_data.get('source', ''),
                source_group=event_data.get('source_group', ''),
                source_url=event_data.get('metadata', {}).get('source_url', ''),
                source_name=event_data.get('metadata', {}).get('source_name', ''),
                venue_name=event_data.get('metadata', {}).get('venue', {}).get('name', ''),
                venue_type=event_data.get('metadata', {}).get('venue', {}).get('type', ''),
                is_academic=is_academic_event(event_data),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(db_event)
        
        db.commit()
        logging.info(f"Saved {len(events)} events to database")
        
    except Exception as e:
        logging.error(f"Error saving events to database: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main scraping and database update function."""
    logging.info("Starting academic events scraping...")
    
    # Run all scrapers
    all_results = run_all_scrapers()
    
    # Flatten results
    all_events = [event for events in all_results.values() for event in events]
    
    # Filter for academic events
    academic_events = [event for event in all_events if is_academic_event(event)]
    
    logging.info(f"Total events scraped: {len(all_events)}")
    logging.info(f"Academic events: {len(academic_events)}")
    
    # Save to database
    save_events_to_database(academic_events)
    
    logging.info("Scraping and database update complete!")

if __name__ == "__main__":
    main()
