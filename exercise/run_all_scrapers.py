#!/usr/bin/env python3
"""
Run all exercise/community event scrapers
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_scraper(scraper_path: Path) -> tuple[bool, int]:
    """Run a scraper and return (success, event_count)"""
    try:
        result = subprocess.run(
            [sys.executable, str(scraper_path)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=scraper_path.parent
        )
        
        if result.returncode != 0:
            print(f"  [FAIL] Failed: {result.stderr[:100]}")
            return False, 0
        
        # Try to count events from output file
        output_files = [
            scraper_path.parent / 'data' / f"{scraper_path.stem.replace('_scraper', '')}_events.json",
            scraper_path.parent / f"{scraper_path.stem}_debug.json",
        ]
        
        for output_file in output_files:
            if output_file.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    events = data if isinstance(data, list) else data.get('events', [])
                    return True, len(events)
                except:
                    pass
        
        return True, 0
        
    except subprocess.TimeoutExpired:
        print("  [FAIL] Timeout after 180s")
        return False, 0
    except Exception as e:
        print(f"  [FAIL] Error: {str(e)[:100]}")
        return False, 0

def main():
    print("="*60)
    print("Running Exercise/Community Event Scrapers")
    print("="*60)
    
    scrapers_dir = Path(__file__).parent / 'scrapers'
    
    # Find all scraper files
    scrapers = [
        'bryant_park.py',
        'google_calendar_scraper.py',
        'ics_calendar_scraper.py',
        'nyc_parks_scraper.py',
        'shirley_chisholm.py'
    ]
    
    results = []
    total_events = 0
    
    for scraper_file in scrapers:
        scraper_path = scrapers_dir / scraper_file
        
        if not scraper_path.exists():
            print(f"[WARN] {scraper_file}: Not found, skipping")
            continue
        
        print(f"\n[RUN] Running {scraper_file}...")
        success, event_count = run_scraper(scraper_path)
        
        if success:
            print(f"  [PASS] Success: {event_count} events")
            results.append((scraper_file, 'success', event_count))
            total_events += event_count
        else:
            results.append((scraper_file, 'failed', 0))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r[1] == 'success']
    failed = [r for r in results if r[1] == 'failed']
    
    print(f"\nSuccessful: {len(successful)}/{len(results)}")
    print(f"Total events: {total_events}")
    
    if failed:
        print(f"\nFailed scrapers:")
        for scraper, _, _ in failed:
            print(f"  - {scraper}")
    
    # Combine events if there's a tag processor
    try:
        from scrapers.tag_processor import main as process_tags
        print("\n[TAGS] Processing tags...")
        process_tags()
        print("  [PASS] Tags processed")
    except ImportError:
        pass
    except Exception as e:
        print(f"  [WARN] Tag processing failed: {e}")
    
    return len(failed) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

