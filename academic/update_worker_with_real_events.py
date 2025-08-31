#!/usr/bin/env python3
"""
Update Cloudflare Worker with Real Events
This script replaces the placeholder events with all 603 real events
"""

import json
import re
from pathlib import Path

def update_worker_file():
    """Update the cloudflare-worker.js file with real events"""
    
    print("🔄 Loading converted events...")
    
    # Load the converted events
    with open('worker_events.json', 'r', encoding='utf-8') as f:
        worker_data = json.load(f)
    
    events = worker_data.get('events', [])
    print(f"📊 Loaded {len(events)} events")
    
    # Read the current worker file
    worker_file = 'cloudflare-worker.js'
    with open(worker_file, 'r', encoding='utf-8') as f:
        worker_content = f.read()
    
    # Create the events array as a JavaScript string
    events_js = json.dumps(events, indent=2, ensure_ascii=False)
    
    # Replace the placeholder events array
    # Find the start and end of the academicEvents array
    start_pattern = r'const academicEvents = \['
    end_pattern = r'\];\s*\n\n// TODO:'
    
    # Create the new events array content
    new_events_content = f"""const academicEvents = {events_js};

// Auto-generated events data - {len(events)} events
// Generated at: {worker_data.get('generated_at', 'unknown')}
// This data is automatically updated weekly by the scraping process"""
    
    # Replace the content
    updated_content = re.sub(
        start_pattern + r'.*?' + end_pattern,
        new_events_content,
        worker_content,
        flags=re.DOTALL
    )
    
    # Write the updated worker file
    with open(worker_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Updated {worker_file} with {len(events)} real events")
    
    # Create a backup of the original
    backup_file = f"{worker_file}.backup"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(worker_content)
    
    print(f"💾 Created backup: {backup_file}")
    
    return len(events)

def main():
    """Main update function"""
    
    print("🚀 Updating Cloudflare Worker with Real Events")
    print("=" * 60)
    
    try:
        # Check if worker_events.json exists
        if not Path('worker_events.json').exists():
            print("❌ worker_events.json not found!")
            print("   Run convert_events_for_worker.py first")
            return False
        
        # Update the worker file
        event_count = update_worker_file()
        
        print(f"\n🎉 Successfully updated worker with {event_count} events!")
        print(f"📝 Next step: Deploy the updated worker with:")
        print(f"   npx wrangler deploy --env=\"\"")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Update failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
