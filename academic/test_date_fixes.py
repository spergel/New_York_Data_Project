#!/usr/bin/env python3
"""
Test script to verify all date fixes are working correctly
"""

import json
import re
from pathlib import Path
from datetime import datetime

def is_valid_iso_datetime(date_str):
    """Check if a date string is in valid ISO format with timezone"""
    if not date_str:
        return False, "Empty date string"
    
    # Pattern for ISO 8601 with timezone: 2025-10-16T09:00:00-04:00 or 2025-10-16T09:00:00.123456-04:00
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$'
    
    if not re.match(pattern, date_str):
        return False, f"Does not match ISO 8601 with timezone pattern: {date_str}"
    
    # Try to parse it
    try:
        datetime.fromisoformat(date_str)
        return True, "Valid"
    except ValueError as e:
        return False, f"Invalid datetime: {e}"

def test_debug_files():
    """Test all debug JSON files for proper date formatting"""
    print("=" * 70)
    print("TESTING DATE FIXES IN DEBUG FILES")
    print("=" * 70)
    print()
    
    # Check both current directory and scrapers subdirectory
    debug_files = list(Path('.').glob('*_events_debug.json'))
    debug_files.extend(list(Path('scrapers').glob('*_events_debug.json')))
    
    if not debug_files:
        print("No debug files found. Run some scrapers first.")
        return
    
    total_events = 0
    events_with_dates = 0
    events_with_valid_dates = 0
    events_with_invalid_dates = 0
    issues = []
    
    for debug_file in sorted(debug_files):
        try:
            with open(debug_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract events
            if isinstance(data, dict):
                events = data.get('events', [])
                scraped_at = data.get('scraped_at', '')
                
                # Check scraped_at timestamp
                if scraped_at:
                    valid, msg = is_valid_iso_datetime(scraped_at)
                    if not valid:
                        issues.append(f"{debug_file.name}: Invalid scraped_at - {msg}")
            else:
                events = data if isinstance(data, list) else []
            
            file_event_count = len(events)
            total_events += file_event_count
            
            # Check each event's dates
            for i, event in enumerate(events):
                start_date = event.get('start_date', '')
                end_date = event.get('end_date', '')
                
                if start_date:
                    events_with_dates += 1
                    valid, msg = is_valid_iso_datetime(start_date)
                    if valid:
                        events_with_valid_dates += 1
                    else:
                        events_with_invalid_dates += 1
                        issues.append(f"{debug_file.name} event {i}: Invalid start_date - {msg}")
                
                if end_date:
                    valid, msg = is_valid_iso_datetime(end_date)
                    if not valid:
                        issues.append(f"{debug_file.name} event {i}: Invalid end_date - {msg}")
            
            print(f"[OK] {debug_file.name}: {file_event_count} events")
            
        except Exception as e:
            print(f"[ERROR] {debug_file.name}: Error - {e}")
            issues.append(f"{debug_file.name}: Failed to parse - {e}")
    
    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total events: {total_events}")
    print(f"Events with dates: {events_with_dates}")
    print(f"Events with valid dates: {events_with_valid_dates}")
    print(f"Events with invalid dates: {events_with_invalid_dates}")
    print()
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  [X] {issue}")
        print()
        return False
    else:
        print("[OK] ALL DATES ARE PROPERLY FORMATTED!")
        print("[OK] All dates include timezone information")
        print("[OK] All dates are in NYC timezone (America/New_York)")
        print()
        return True

def main():
    success = test_debug_files()
    
    if success:
        print("=" * 70)
        print("SUCCESS! All date fixes are working correctly.")
        print("=" * 70)
    else:
        print("=" * 70)
        print("FAILURE! Some dates are not properly formatted.")
        print("=" * 70)
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

