import json

def analyze_event_quality():
    with open('events_test/academic_events_filtered.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    print(f"Total academic events: {len(events)}")
    print("\n" + "="*80)
    
    # Analyze by source
    sources = {}
    for event in events:
        source = event.get('source', 'unknown')
        if source not in sources:
            sources[source] = []
        sources[source].append(event)
    
    print("EVENT QUALITY ANALYSIS BY SOURCE:")
    print("="*80)
    
    for source, events in sources.items():
        print(f"\n{source.upper()} ({len(events)} events):")
        print("-" * 40)
        
        # Show first 5 events from each source
        for i, event in enumerate(events[:5]):
            name = event.get('name', 'No name')
            description = event.get('description', '')[:100] + "..." if len(event.get('description', '')) > 100 else event.get('description', '')
            venue = event.get('metadata', {}).get('venue', {}).get('name', 'No venue')
            
            print(f"{i+1}. {name}")
            print(f"   Venue: {venue}")
            print(f"   Description: {description}")
            print()
        
        if len(events) > 5:
            print(f"... and {len(events) - 5} more events")
        print()

if __name__ == "__main__":
    analyze_event_quality()
