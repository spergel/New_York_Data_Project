import json

def analyze_filtered_events():
    with open('events_test/academic_events_filtered.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data['events']
    print(f"Total academic events: {len(events)}")
    
    # Count by source
    sources = {}
    for event in events:
        source = event['source']
        sources[source] = sources.get(source, 0) + 1
    
    print("\nEvents by source:")
    for source, count in sorted(sources.items()):
        print(f"  {source}: {count}")
    
    # Show some examples
    print("\nExample academic events:")
    for i, event in enumerate(events[:10]):
        print(f"{i+1}. {event['name']} ({event['source']})")
        print(f"   Date: {event['startDate']}")
        print(f"   Venue: {event['metadata']['venue']['name']}")
        print()

if __name__ == "__main__":
    analyze_filtered_events()
