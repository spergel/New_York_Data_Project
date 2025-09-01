#!/usr/bin/env python3
"""
Combine worker template with events data
"""

import json

def main():
    """Combine worker template with events data"""
    try:
        # Load worker events
        with open('worker_events.json', 'r', encoding='utf-8') as f:
            worker_data = json.load(f)
        
        events = worker_data.get('events', [])
        print(f"📝 Generating updated worker code with {len(events)} events...")
        
        # Create the worker code
        worker_code = f"""// Auto-generated events data - {len(events)} events
// Generated at: {worker_data.get('generated_at', 'unknown')}
// This file is automatically updated weekly by the scraping process

const academicEvents = {json.dumps(events, indent=2, ensure_ascii=False)};

// Export for use in main worker
export {{ academicEvents }};
"""
        
        # Save worker code
        with open('worker_events_code.js', 'w', encoding='utf-8') as f:
            f.write(worker_code)
        
        print(f"📝 Generated updated worker code in worker_events_code.js")
        
    except FileNotFoundError:
        print("❌ worker_events.json not found. Run convert_events_for_worker.py first.")
    except Exception as e:
        print(f"❌ Error generating worker code: {e}")

if __name__ == "__main__":
    main()
