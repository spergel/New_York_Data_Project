#!/usr/bin/env python3
"""
Test script for event_utils.py
"""

import sys
import os
from utils.event_utils import determine_event_categories, MainCategory

def test_event_categorization():
    """Test the event categorization function"""
    # Test cases
    test_events = [
        {
            "title": "AI in Healthcare: Latest Advances",
            "description": "A lecture on the latest advances in artificial intelligence applications in healthcare. Professor Smith will discuss recent research and future directions."
        },
        {
            "title": "Symphony Orchestra Concert",
            "description": "Join us for a night of classical music featuring Beethoven's Symphony No. 5 and Mozart's Piano Concerto No. 21."
        },
        {
            "title": "Data Science Workshop",
            "description": "A hands-on workshop exploring data analysis techniques and machine learning algorithms. Bring your laptop!"
        },
        {
            "title": "Community Event",
            "description": "Join us for a community gathering with food and activities."
        }
    ]
    
    # Process each test event
    for i, event in enumerate(test_events):
        main_categories, event_types = determine_event_categories(event)
        
        print(f"\nEvent {i+1}: {event['title']}")
        print(f"Description: {event['description']}")
        print(f"Main Categories: {main_categories}")
        print(f"Event Types: {event_types}")
        
        # Verify expected results
        if i == 0:  # AI in Healthcare
            assert MainCategory.ACADEMIC.value in main_categories, "Expected Academic category for AI lecture"
            assert "Lecture" in event_types, "Expected Lecture event type for AI lecture"
        elif i == 1:  # Symphony Orchestra Concert
            assert MainCategory.PERFORMANCE.value in main_categories, "Expected Performance category for concert"
            assert "Concert" in event_types, "Expected Concert event type for orchestra event"
        elif i == 2:  # Data Science Workshop
            assert MainCategory.ACADEMIC.value in main_categories, "Expected Academic category for workshop"
            assert "Workshop" in event_types, "Expected Workshop event type for data science workshop"
        elif i == 3:  # Community Event
            assert MainCategory.OTHER.value in main_categories, "Expected Other category for community event"
            assert len(event_types) == 0, "Expected no specific event types for community event"
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_event_categorization() 