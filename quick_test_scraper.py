#!/usr/bin/env python3
"""
Quick test script for individual scrapers
Usage: python quick_test_scraper.py <scraper_file>
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def test_scraper(scraper_path: str):
    """Test a single scraper"""
    scraper = Path(scraper_path)
    
    if not scraper.exists():
        print(f"[ERROR] Scraper not found: {scraper_path}")
        return False
    
    print(f"[RUN] Running {scraper.name}...")
    print("-" * 60)
    
    # Run the scraper
    try:
        result = subprocess.run(
            [sys.executable, str(scraper.absolute())],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode != 0:
            print(f"[FAIL] Scraper failed with return code {result.returncode}")
            print(f"\nError output:\n{result.stderr}")
            return False
        
        print("[PASS] Scraper ran successfully\n")
        
        # Print stdout if verbose
        if result.stdout:
            print("Output:")
            print(result.stdout[:500])  # First 500 chars
        
    except subprocess.TimeoutExpired:
        print("[FAIL] Scraper timed out after 180 seconds")
        return False
    except Exception as e:
        print(f"[FAIL] Error running scraper: {e}")
        return False
    
    # Find and validate output
    print("\n" + "="*60)
    print("[VALIDATE] Validating Output")
    print("="*60)
    
    # Look for output files
    possible_outputs = [
        scraper.parent / f"{scraper.stem}_debug.json",
        scraper.parent / 'data' / f"{scraper.stem}_events.json",
        scraper.parent.parent / f"{scraper.stem}_debug.json",
        scraper.parent.parent / 'data' / f"{scraper.stem.replace('_scraper', '')}_events.json",
    ]
    
    output_file = None
    for possible in possible_outputs:
        if possible.exists():
            output_file = possible
            break
    
    if not output_file:
        print(f"[WARN] No output file found. Checked:")
        for p in possible_outputs:
            print(f"   - {p}")
        return False
    
    print(f"[INFO] Output file: {output_file}")
    
    # Load and validate events
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract events
        if isinstance(data, list):
            events = data
        elif isinstance(data, dict) and 'events' in data:
            events = data['events']
        else:
            print(f"[ERROR] Unexpected data format: {type(data)}")
            return False
        
        print(f"\n[INFO] Found {len(events)} events")
        
        if len(events) == 0:
            print("[WARN] No events extracted")
            return False
        
        # Validate events
        print("\n" + "-"*60)
        print("[SAMPLE] Sample Events (first 3)")
        print("-"*60)
        
        for i, event in enumerate(events[:3]):
            print(f"\nEvent {i+1}:")
            print(f"  Title: {event.get('title', 'MISSING')[:70]}")
            print(f"  Date: {event.get('start_date', 'MISSING')}")
            print(f"  Location: {event.get('location', 'MISSING')[:50]}")
            print(f"  Source: {event.get('source', 'MISSING')}")
            print(f"  URL: {event.get('url', 'MISSING')[:60]}")
            
            # Check for issues
            issues = []
            if not event.get('title'):
                issues.append("Missing title")
            if not event.get('start_date'):
                issues.append("Missing start_date")
            if not event.get('description'):
                issues.append("Missing description")
            if not event.get('location'):
                issues.append("Missing location")
            if not event.get('url'):
                issues.append("Missing URL")
            
            if issues:
                print(f"  [WARN] Issues: {', '.join(issues)}")
        
        # Summary
        print("\n" + "="*60)
        print("[SUMMARY] Summary")
        print("="*60)
        
        # Count issues
        missing_dates = sum(1 for e in events if not e.get('start_date'))
        missing_desc = sum(1 for e in events if not e.get('description'))
        missing_loc = sum(1 for e in events if not e.get('location'))
        missing_url = sum(1 for e in events if not e.get('url'))
        
        print(f"Total events: {len(events)}")
        print(f"Missing start_date: {missing_dates}")
        print(f"Missing description: {missing_desc}")
        print(f"Missing location: {missing_loc}")
        print(f"Missing URL: {missing_url}")
        
        # Pass/fail
        if missing_dates > 0:
            print("\n[FAIL] Test FAILED: Events missing required dates")
            return False
        elif missing_desc > len(events) * 0.5:
            print(f"\n[WARN] Test PARTIAL: {missing_desc} events missing descriptions")
            return True
        else:
            print("\n[PASS] Test PASSED")
            return True
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in output file: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error validating output: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_test_scraper.py <scraper_file>")
        print("\nExamples:")
        print("  python quick_test_scraper.py academic/scrapers/columbia_events.py")
        print("  python quick_test_scraper.py tech/scrapers/pioneer_works_scraper.py")
        sys.exit(1)
    
    scraper_path = sys.argv[1]
    success = test_scraper(scraper_path)
    sys.exit(0 if success else 1)

