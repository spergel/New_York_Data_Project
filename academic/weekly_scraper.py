#!/usr/bin/env python3
"""
Weekly Academic Events Scraper
This script runs all scrapers and updates the Cloudflare worker data
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add the scrapers directory to the path
sys.path.append('scrapers')

def run_scrapers():
    """Run all available scrapers"""
    print("Starting weekly scraping process...")
    
    # List of ALL WORKING scraper files (updated and tested)
    scrapers = [
        'columbia_classics_events.py',          # [PASS] 23 events
        'columbia_general_events.py',           # [PASS] 100 events
        'columbia_math_events.py',              # [PASS] 2 events
        'cooper_union_events.py',               # [PASS] 2 events
        'cornell_tech_events.py',               # [PASS] 2 events
        'fordham_events.py',                    # [PASS] 6 events (Google Calendar)
        'gallatin_events.py',                   # [PASS] 21 events
        'isaw_events.py',                       # [PASS] 5 events
        'jtsa_events.py',                       # [PASS] 10 events
        'juilliard_events.py',                  # [WARN] Cloudflare blocked
        'miller_events.py',                     # [PASS] 57 events
        'new_school_events.py',                 # [PASS] 70 events
        'nyu_api_events.py',                    # [PASS] 43 events (NEW API)
        'nyu_cims_events.py',                   # [PASS] 38 events
        'nyu_education_events.py',              # [PASS] 2 events
        'nyu_engineering.py',                  # [PASS] 50+ events
        'nyu_law_events.py',                    # [PASS] 9 events
        'nyu_medicine_events.py',               # [PASS] 2 events
        'nyu_neuroscience_events.py',           # [PASS] 11 events (NEW)
        'nyu_physics_events.py',                # [PASS] 6 events (NEW)
        'nyu_steinhardt_events.py',             # [PASS] 6 events (NEW)
        'nyu_steinhardt_music_events.py',       # [PASS] 17 events (NEW)
        'nyu_stern_events.py',                  # [PASS] 8 events
        'pratt_events.py',                      # [PASS] 4 events
        'simons_foundation_events.py',         # [PASS] 2 events
        'luma_events.py'                        # [PASS] DeSciNYC events
    ]
    
    # TODO: Fix these remaining broken scrapers to get even more events:
    # - brooklyn_college_events.py (no_output)
    # - columbia_history_events.py (no_output)
    # - columbia_social_difference_events.py (no_output)
    # - juilliard_events.py (no_output)
    # - stjohns_events.py (no_output)
    
    # TODO: Fix these scrapers that are getting crap data (missing dates, descriptions, past events):
    # - nyu_stern_events.py (missing end dates, getting past events from March-June 2025)
    # - pratt_events.py (NO start dates, NO end dates, NO descriptions - just event names)
    # - cooper_union_events.py (missing end dates, only getting 2 events, poor date parsing)
    
    successful_scrapers = []
    failed_scrapers = []
    
    for scraper in scrapers:
        scraper_path = Path('scrapers') / scraper
        if scraper_path.exists():
            print(f"Running {scraper}...")
            try:
                # Run the scraper
                result = subprocess.run(
                    ['python', str(scraper_path)],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=Path.cwd()  # Run from current directory
                )
                
                if result.returncode == 0:
                    print(f"[SUCCESS] {scraper} completed successfully")
                    successful_scrapers.append(scraper)
                else:
                    print(f"[FAILED] {scraper} failed with return code {result.returncode}")
                    print(f"Error: {result.stderr}")
                    failed_scrapers.append(scraper)
                    
            except subprocess.TimeoutExpired:
                print(f"[TIMEOUT] {scraper} timed out after 5 minutes")
                failed_scrapers.append(scraper)
            except Exception as e:
                print(f"[CRASH] {scraper} crashed: {e}")
                failed_scrapers.append(scraper)
        else:
            print(f"[WARNING] {scraper} not found, skipping")

    print(f"\n=== SCRAPING SUMMARY ===")
    print(f"SUCCESSFUL: {len(successful_scrapers)}")
    print(f"FAILED: {len(failed_scrapers)}")
    
    if failed_scrapers:
        print(f"Failed scrapers: {', '.join(failed_scrapers)}")
    
    return successful_scrapers, failed_scrapers

def combine_events():
    """Combine all scraped events into one file"""
    print("Combining events from all sources...")
    
    all_events = []
    event_sources = {}
    
    # Look for event files in the current directory (where scrapers save them)
    for event_file in Path('.').glob('*_events_debug.json'):
        try:
            with open(event_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            if isinstance(events, list):
                all_events.extend(events)
                event_sources[event_file.stem] = len(events)
            elif isinstance(events, dict) and 'events' in events:
                all_events.extend(events['events'])
                event_sources[event_file.stem] = len(events['events'])
                
        except Exception as e:
            print(f"[WARNING] Error reading {event_file}: {e}")
    
    # Remove duplicates based on event ID
    unique_events = {}
    for event in all_events:
        event_id = event.get('id') or event.get('event_id')
        if event_id and event_id not in unique_events:
            unique_events[event_id] = event
    
    combined_events = list(unique_events.values())
    
    print(f"Combined {len(combined_events)} unique events from {len(event_sources)} sources")
    
    # Save combined events
    combined_data = {
        "scraped_at": datetime.now().isoformat(),
        "total_events": len(combined_events),
        "event_sources": event_sources,
        "events": combined_events
    }
    
    with open('scraped_events.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved combined events to scraped_events.json")
    return combined_events

def convert_for_worker(events):
    """Convert events to worker format"""
    print("Converting events for Cloudflare worker...")
    
    # Import the conversion function
    from convert_events_for_worker import convert_event
    
    converted_events = []
    for i, event in enumerate(events):
        if i % 100 == 0:
            print(f"Converting event {i+1}/{len(events)}...")
        
        converted_event = convert_event(event)
        converted_events.append(converted_event)
    
    print(f"[SUCCESS] Converted {len(converted_events)} events for worker")
    
    # Save worker-ready events
    worker_data = {
        "generated_at": datetime.now().isoformat(),
        "total_events": len(converted_events),
        "events": converted_events
    }
    
    with open('worker_events.json', 'w', encoding='utf-8') as f:
        json.dump(worker_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved worker events to worker_events.json")
    return converted_events

def update_worker_code(events):
    """Generate updated worker code with new events"""
    print("Generating updated worker code...")
    
    # Create the worker code snippet
    worker_code = f"""// Auto-generated events data - {len(events)} events
// Generated at: {datetime.now().isoformat()}
// This file is automatically updated weekly by the scraping process

const academicEvents = {json.dumps(events, indent=2, ensure_ascii=False)};

// Export for use in main worker
export {{ academicEvents }};
"""
    
    # Save worker code
    with open('worker_events_code.js', 'w', encoding='utf-8') as f:
        f.write(worker_code)
    
    print(f"Generated updated worker code in worker_events_code.js")

def deploy_worker():
    """Deploy the updated worker to Cloudflare"""
    print("Deploying updated worker to Cloudflare...")
    
    try:
        result = subprocess.run(['npx', 'wrangler', 'deploy'],
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("[PASS] Worker deployed successfully!")
            print("[INFO] API available at: https://nyc-academic-events-api.spergel-joshua.workers.dev")
        else:
            print(f"[FAIL] Worker deployment failed: {result.stderr}")

    except Exception as e:
        print(f"[ERROR] Error deploying worker: {e}")

def main():
    """Main weekly scraping process"""
    start_time = datetime.now()
    print(f"Starting weekly scraping at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Step 1: Run all scrapers
        successful_scrapers, failed_scrapers = run_scrapers()
        
        # Step 2: Combine events
        combined_events = combine_events()
        
        # Step 3: Convert for worker
        worker_events = convert_for_worker(combined_events)
        
        # Step 4: Update worker code
        update_worker_code(worker_events)
        
        # Step 5: Deploy worker
        deploy_worker()
        
        # Summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("[SUCCESS] WEEKLY SCRAPING COMPLETED SUCCESSFULLY!")
        print(f"[INFO] Total duration: {duration}")
        print(f"[PASS] Successful scrapers: {len(successful_scrapers)}")
        print(f"[FAIL] Failed scrapers: {len(failed_scrapers)}")
        print(f"[INFO] Total events: {len(worker_events)}")
        print(f"[INFO] API updated and deployed")

        if failed_scrapers:
            print(f"\n[WARN] Failed scrapers: {', '.join(failed_scrapers)}")

    except Exception as e:
        print(f"\n[ERROR] Weekly scraping failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
