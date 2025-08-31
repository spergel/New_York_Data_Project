#!/usr/bin/env python3
"""
Data Quality Checker for NYC Academic Events
Examines scraped events data for quality issues and provides insights
"""

import json
import os
from datetime import datetime
from collections import Counter
import re

def load_json_file(filepath):
    """Load and parse a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def check_event_quality(event, event_num):
    """Check individual event for quality issues"""
    issues = []
    
    # Check required fields
    required_fields = ['id', 'name', 'type', 'start_date']
    for field in required_fields:
        if field not in event:
            issues.append(f"Missing required field: {field}")
        elif not event[field]:
            issues.append(f"Empty required field: {field}")
    
    # Check ID format
    if 'id' in event and event['id']:
        if not re.match(r'^evt_[a-z_]+_[a-f0-9]+$', event['id']):
            issues.append(f"Invalid ID format: {event['id']}")
    
    # Check dates
    if 'start_date' in event and event['start_date']:
        try:
            datetime.fromisoformat(event['start_date'].replace('Z', '+00:00'))
        except:
            issues.append(f"Invalid start_date format: {event['start_date']}")
    
    if 'end_date' in event and event['end_date']:
        try:
            datetime.fromisoformat(event['end_date'].replace('Z', '+00:00'))
        except:
            issues.append(f"Invalid end_date format: {event['end_date']}")
    
    # Check description length
    if 'description' in event and event['description']:
        desc_length = len(event['description'])
        if desc_length < 10:
            issues.append(f"Very short description ({desc_length} chars)")
        elif desc_length > 5000:
            issues.append(f"Very long description ({desc_length} chars)")
    
    # Check for HTML in description
    if 'description' in event and event['description']:
        if re.search(r'<[^>]+>', event['description']):
            issues.append("Contains HTML tags")
    
    # Check venue information
    if 'metadata' in event and 'venue' in event['metadata']:
        venue = event['metadata']['venue']
        if not venue.get('name'):
            issues.append("Missing venue name")
    
    return issues

def analyze_data_quality(data, filename):
    """Analyze overall data quality"""
    print(f"\n🔍 Analyzing: {filename}")
    print("=" * 60)
    
    if not data:
        print("❌ No data to analyze")
        return
    
    # Basic stats
    if 'events' in data:
        events = data['events']
        total_events = len(events)
        print(f"📊 Total Events: {total_events}")
        
        if 'scraped_at' in data:
            print(f"🕒 Last Scraped: {data['scraped_at']}")
    else:
        events = data
        total_events = len(events)
        print(f"📊 Total Events: {total_events}")
    
    if total_events == 0:
        print("❌ No events found")
        return
    
    # Quality analysis
    quality_issues = []
    field_stats = Counter()
    type_stats = Counter()
    category_stats = Counter()
    source_stats = Counter()
    
    for i, event in enumerate(events):
        # Check individual event quality
        issues = check_event_quality(event, i)
        if issues:
            quality_issues.append((i, event.get('name', 'Unknown'), issues))
        
        # Collect field statistics
        for field in event.keys():
            field_stats[field] += 1
        
        # Collect type statistics
        if 'type' in event:
            type_stats[event['type']] += 1
        
        # Collect category statistics
        if 'category' in event and event['category']:
            for cat in event['category']:
                category_stats[cat] += 1
        
        # Collect source statistics
        if 'metadata' in event and 'source_name' in event['metadata']:
            source_stats[event['metadata']['source_name']] += 1
    
    # Report findings
    print(f"\n📈 Field Coverage:")
    for field, count in field_stats.most_common():
        percentage = (count / total_events) * 100
        print(f"  {field}: {count}/{total_events} ({percentage:.1f}%)")
    
    print(f"\n🏷️ Event Types:")
    for event_type, count in type_stats.most_common():
        percentage = (count / total_events) * 100
        print(f"  {event_type}: {count} ({percentage:.1f}%)")
    
    print(f"\n📚 Categories:")
    for category, count in category_stats.most_common(10):
        percentage = (count / total_events) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    print(f"\n🏛️ Sources:")
    for source, count in source_stats.most_common():
        percentage = (count / total_events) * 100
        print(f"  {source}: {count} ({percentage:.1f}%)")
    
    # Quality issues report
    if quality_issues:
        print(f"\n⚠️ Quality Issues Found: {len(quality_issues)}")
        print("First 10 issues:")
        for i, (event_num, name, issues) in enumerate(quality_issues[:10]):
            print(f"  Event {event_num}: {name[:50]}...")
            for issue in issues:
                print(f"    - {issue}")
        if len(quality_issues) > 10:
            print(f"    ... and {len(quality_issues) - 10} more issues")
    else:
        print(f"\n✅ No quality issues found!")
    
    # Sample events
    print(f"\n📝 Sample Events:")
    for i, event in enumerate(events[:3]):
        print(f"\n  Event {i+1}:")
        print(f"    Name: {event.get('name', 'N/A')[:60]}...")
        print(f"    Type: {event.get('type', 'N/A')}")
        print(f"    Date: {event.get('start_date', 'N/A')}")
        print(f"    Venue: {event.get('metadata', {}).get('venue', {}).get('name', 'N/A')}")

def main():
    """Main function to check all data files"""
    print("🔍 NYC Academic Events - Data Quality Checker")
    print("=" * 60)
    
    # Check main scraped events file
    main_file = "scraped_events.json"
    if os.path.exists(main_file):
        data = load_json_file(main_file)
        analyze_data_quality(data, main_file)
    else:
        print(f"❌ Main file not found: {main_file}")
    
    # Check institution-specific files
    institution_files = [
        "nyu_engineering_events_debug.json",
        "cims_events_debug.json", 
        "new_school_events_debug.json",
        "jtsa_events_debug.json",
        "isaw_events_debug.json",
        "gallatin_events_debug.json",
        "cornell_tech_events_debug.json",
        "simons_foundation_events.json"
    ]
    
    for filename in institution_files:
        if os.path.exists(filename):
            data = load_json_file(filename)
            analyze_data_quality(data, filename)
        else:
            print(f"⚠️ File not found: {filename}")
    
    print(f"\n🎯 Data Quality Check Complete!")
    print("Check the output above for any issues or patterns in your data.")

if __name__ == "__main__":
    main()
