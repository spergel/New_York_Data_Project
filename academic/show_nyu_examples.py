import json

def show_nyu_examples():
    with open('events_test/academic_events_filtered.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    nyu_events = [e for e in events if e.get('source') == 'nyu']
    
    print(f"NYU Academic Events (showing 10-25):")
    print("="*60)
    
    for i, event in enumerate(nyu_events[10:25]):
        name = event.get('name', 'No name')
        venue = event.get('metadata', {}).get('venue', {}).get('name', 'No venue')
        print(f"{i+11}. {name}")
        print(f"    Venue: {venue}")
        print()

if __name__ == "__main__":
    show_nyu_examples()
