import json
import os
from pathlib import Path
import re

# Exercise type keywords mapping
EXERCISE_KEYWORDS = {
    'walking': ['walk', 'walking', 'hike', 'hiking'],
    'running': ['run', 'running', 'jog', 'jogging', 'sprint'],
    'dance': ['dance', 'zumba', 'soca', 'salsa', 'bachata'],
    'cycling': ['cycle', 'cycling', 'spin', 'spinning', 'spin class'],
    'yoga': ['yoga', 'yoga class', 'yoga studio', 'yoga studio class', 'hatha'],
    'pilates': ['pilates', 'pilates class', 'pilates studio', 'pilates studio class', 'pilates class', 'pilates studio'],
    'body workout': ['workout', 'fitness', 'strength', 'training', 'cardio', 'exercise', 'bootcamp'],
    'rollerblading': ['rollerblade', 'rollerblading', 'skate', 'skating']
}

def determine_exercise_type(text):
    """Determine exercise type based on text content"""
    text = text.lower()
    
    for exercise_type, keywords in EXERCISE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return exercise_type
    
    return 'other'

def process_file(file_path):
    """Process a single JSON file and return processed events"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON formats
        if isinstance(data, dict) and 'events' in data:
            events = data['events']
        elif isinstance(data, list):
            events = data
        elif isinstance(data, dict):
            events = [data]
        else:
            print(f"Warning: Unexpected data format in {file_path}")
            return []
        
        processed_events = []
        
        for event in events:
            if isinstance(event, dict) and 'name' in event:
                # Combine name and description for better context
                text_to_analyze = f"{event.get('name', '')} {event.get('description', '')}"
                exercise_type = determine_exercise_type(text_to_analyze)
                
                # Update tags to only include exercise type
                event['tags'] = [exercise_type]
                # Set category to exercise
                event['category'] = ["exercise"]
                processed_events.append(event)
        
        return processed_events
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {file_path}: {str(e)}")
        return []
    except Exception as e:
        print(f"Warning: Error processing {file_path}: {str(e)}")
        return []

def setup_directories():
    """Set up the required directories"""
    # Get the script's directory and set up paths
    script_dir = Path(__file__).parent.absolute()  # exercise directory
    
    # Set up input and output directories
    input_dir = script_dir / 'scrapers' / 'data'
    output_dir = script_dir / 'data'
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"Warning: Input directory {input_dir} does not exist")
        return input_dir, output_dir
        
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    return input_dir, output_dir

def main():
    # Set up directories and get paths
    input_dir, output_dir = setup_directories()
    
    all_events = []
    
    # Process all JSON files in the input directory
    json_files = list(input_dir.glob('*.json'))
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return
    
    for file_path in json_files:
        try:
            print(f"Processing {file_path}")
            events = process_file(file_path)
            all_events.extend(events)
            print(f"Successfully processed {len(events)} events from {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Save all processed events to a single output file
    output_file = output_dir / 'events.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_events, f, indent=2)
    
    print(f"\nAll events have been processed and saved to {output_file}")
    print(f"Total events processed: {len(all_events)}")

if __name__ == "__main__":
    main() 