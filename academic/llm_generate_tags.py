import pandas as pd
import json
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum, auto
from sentence_transformers import SentenceTransformer, util
import torch  # Import torch
import os
from itertools import cycle
import sys
import numpy as np
import logging

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.event_utils import MainCategory

# Define event types for categorization
class AcademicType(Enum):
    LECTURE = "Lecture"
    CONFERENCE = "Conference"
    RESEARCH_PRESENTATION = "Research Presentation"
    PANEL_DISCUSSION = "Panel Discussion"
    SYMPOSIUM = "Symposium"
    SEMINAR = "Seminar"
    WORKSHOP = "Workshop"
    DATA_SCIENCE = "Data Science"

class PerformanceType(Enum):
    CONCERT = "Concert"
    THEATER = "Theater"
    DANCE = "Dance"
    COMEDY = "Comedy"
    FILM_SCREENING = "Film Screening"
    ART_EXHIBITION = "Art Exhibition"
    LITERARY_READING = "Literary Reading"

# Define academic topics
class AcademicTopic(Enum):
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    DATA_SCIENCE = "Data Science"
    ENGINEERING = "Engineering"
    SCIENCE = "Science"
    MATH = "Math"
    COMPUTER_SCIENCE = "Computer Science"
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"
    ECONOMICS = "Economics"
    POLITICAL_SCIENCE = "Political Science"
    PHILOSOPHY = "Philosophy"
    LITERATURE = "Literature"
    HISTORY = "History"
    LANGUAGE = "Language"
    LAW = "Law"
    MEDICINE = "Medicine"
    RELIGION = "Religion"
    THEOLOGY = "Theology"
    PSYCHOLOGY = "Psychology"
    SOCIAL_WORK = "Social Work"
    EDUCATION = "Education"
    PUBLIC_POLICY = "Public Policy"
    PUBLIC_HEALTH = "Public Health"
    NURSING = "Nursing"
    PHARMACY = "Pharmacy"
    ASTROPHYSICS = "Astrophysics"
    CHEMICAL_PHYSICS = "Chemical Physics"
    ASTRONOMY = "Astronomy"
    ENVIRONMENTAL_SCIENCE = "Environmental Science"
    ANTHROPOLOGY = "Anthropology"
    SOCIOLOGY = "Sociology"
    ARCHAEOLOGY = "Archaeology"
    LINGUISTICS = "Linguistics"
    OTHER = "Other"

academic_topics = [topic.value for topic in AcademicTopic]

class EventTags(BaseModel):
    """Model for event tags."""
    event_id: str
    description: str
    predicted_tags: List[str] = Field(default_factory=list)
    main_categories: List[str] = Field(default_factory=list)
    event_types: List[str] = Field(default_factory=list)
    academic_topics: List[str] = Field(default_factory=list)
    note: Optional[str] = None

def load_model():
    """Load the sentence transformer model."""
    try:
        # Use a smaller model for faster processing
        model_name = "all-MiniLM-L6-v2"
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        raise

def generate_embeddings(model, texts):
    """Generate embeddings for a list of texts."""
    try:
        return model.encode(texts, convert_to_tensor=True)
    except Exception as e:
        logging.error(f"Error generating embeddings: {e}")
        raise

def calculate_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings."""
    return util.cos_sim(embedding1, embedding2).item()

def process_event(model, event: Dict, all_tags: List[str], tag_embeddings):
    """Processes a single event and assigns tags based on similarity."""
    try:
        event_description = event.get('description', '')
        event_title = event.get('title', '')
        event_department = event.get('department', '')

        # Combine relevant text for embedding
        event_text = f"{event_title}. {event_description} {event_department}"
        event_embedding = generate_embeddings(model, [event_text])[0]  # Get embedding for the event

        # Calculate similarities with all tags
        similarities = [calculate_similarity(event_embedding, tag_embedding) for tag_embedding in tag_embeddings]

        # Get the top N most similar tags (e.g., top 5)
        top_n = 5
        top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_n]
        predicted_tags = [all_tags[i] for i in top_indices]

        # Lowercase event text for keyword matching
        lower_event_text = event_text.lower()

        # Initialize categories
        main_categories = []
        event_types = []
        selected_academic_topics = []

        # Directly assign event types and corresponding main categories
        # Academic event types
        if 'lecture' in lower_event_text:
            event_types.append('Lecture')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        if 'conference' in lower_event_text:
            event_types.append('Conference')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        if 'research' in lower_event_text and 'presentation' in lower_event_text:
            event_types.append('Research Presentation')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        if 'panel' in lower_event_text or 'discussion' in lower_event_text:
            event_types.append('Panel Discussion')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        if 'symposium' in lower_event_text:
            event_types.append('Symposium')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        if 'seminar' in lower_event_text:
            event_types.append('Seminar')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        if 'workshop' in lower_event_text:
            event_types.append('Workshop')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        if 'data science' in lower_event_text or 'machine learning' in lower_event_text:
            event_types.append('Data Science')
            main_categories.append(MainCategory.ACADEMIC.value)
            
        # Performance event types
        if 'concert' in lower_event_text or 'music' in lower_event_text:
            event_types.append('Concert')
            main_categories.append(MainCategory.PERFORMANCE.value)
            
        if 'theater' in lower_event_text or 'theatre' in lower_event_text:
            event_types.append('Theater')
            main_categories.append(MainCategory.PERFORMANCE.value)
            
        if 'dance' in lower_event_text:
            event_types.append('Dance')
            main_categories.append(MainCategory.PERFORMANCE.value)
            
        if 'comedy' in lower_event_text:
            event_types.append('Comedy')
            main_categories.append(MainCategory.PERFORMANCE.value)
            
        if 'film' in lower_event_text or 'screening' in lower_event_text:
            event_types.append('Film Screening')
            main_categories.append(MainCategory.PERFORMANCE.value)
            
        # Check for art exhibition specifically (not just 'art' which is too broad)
        if 'exhibition' in lower_event_text:
            event_types.append('Art Exhibition')
            main_categories.append(MainCategory.PERFORMANCE.value)
            
        if 'reading' in lower_event_text or 'literary' in lower_event_text:
            event_types.append('Literary Reading')
            main_categories.append(MainCategory.PERFORMANCE.value)
        
        # If no specific types were found, check for general keywords
        if not event_types:
            # Check for academic keywords
            academic_keywords = ["academic", "study", "education", "professor", "faculty", "university", "college", "department", "school", "institute", "science", "research"]
            
            # Check for performance keywords
            performance_keywords = ["performance", "gallery", "museum", "show", "play", "opera"]
            
            if any(keyword in lower_event_text for keyword in academic_keywords):
                main_categories.append(MainCategory.ACADEMIC.value)
            
            if any(keyword in lower_event_text for keyword in performance_keywords):
                main_categories.append(MainCategory.PERFORMANCE.value)
        
        # If still no categories matched, assign OTHER
        if not main_categories:
            main_categories.append(MainCategory.OTHER.value)

        # Determine Academic Topics (if applicable)
        if MainCategory.ACADEMIC.value in main_categories:
            for topic in AcademicTopic:
                if topic.value.lower() in lower_event_text:
                    selected_academic_topics.append(topic.value)

        # Remove duplicates while preserving order
        main_categories = list(dict.fromkeys(main_categories))
        event_types = list(dict.fromkeys(event_types))

        # Create the EventTags object
        event_tags = EventTags(
            event_id=event['event_id'],
            description=event_text,
            predicted_tags=predicted_tags,
            main_categories=main_categories,
            event_types=event_types,
            academic_topics=selected_academic_topics,
            note="Generated by embedding similarity and keyword matching with direct category assignment."
        )
        
        # Update the event dictionary
        event['assigned_tags'] = event_tags.predicted_tags
        event['main_categories'] = event_tags.main_categories
        event['event_types'] = event_tags.event_types
        event['academic_topics'] = event_tags.academic_topics
        event['tag_note'] = event_tags.note

        return event

    except Exception as e:
        print(f"Error processing event: {e}")
        return event  # Return the event even if there's an error

def assign_event_tags(model, events: List[Dict], all_tags: List[str], tag_embeddings=None):
    """
    Assigns tags to a list of events based on their descriptions.
    
    Args:
        model: The sentence transformer model
        events: List of event dictionaries
        all_tags: List of all possible tags
        tag_embeddings: Pre-computed embeddings for tags (optional)
        
    Returns:
        List of events with tags assigned
    """
    # If tag embeddings not provided, generate them
    if tag_embeddings is None:
        tag_embeddings = generate_embeddings(model, all_tags)
    
    # Process events in batches for efficiency
    processed_events = []
    
    # Create a progress indicator
    total_events = len(events)
    print(f"Processing {total_events} events...")
    
    # Process each event
    for event in events:
        processed_event = process_event(model, event, all_tags, tag_embeddings)
        processed_events.append(processed_event)
    
    return processed_events

def test_assign_event_tags():
    """Test function to demonstrate the event tagging process."""
    # Create some example events
    events = [
        {
            "event_id": "test1",
            "title": "AI in Healthcare: Latest Advances",
            "description": "A lecture on the latest advances in artificial intelligence applications in healthcare. Professor Smith will discuss recent research and future directions.",
            "department": "Computer Science"
        },
        {
            "event_id": "test2",
            "title": "Symphony Orchestra Concert",
            "description": "Join us for a night of classical music featuring Beethoven's Symphony No. 5 and Mozart's Piano Concerto No. 21.",
            "department": "Music Department"
        },
        {
            "event_id": "test3",
            "title": "Data Science Workshop",
            "description": "A hands-on workshop exploring data analysis techniques and machine learning algorithms. Bring your laptop!",
            "department": "Statistics Department"
        },
        {
            "event_id": "test4",
            "title": "Community Event",
            "description": "Join us for a community gathering with food and activities.",
            "department": ""
        }
    ]
    
    # Define some tags for testing
    all_tags = [
        "artificial intelligence", "healthcare", "music", "classical", 
        "data science", "machine learning", "community", "workshop"
    ]
    
    # Load model
    model = load_model()
    
    # Precompute tag embeddings
    tag_embeddings = generate_embeddings(model, all_tags)
    
    # Process events
    processed_events = assign_event_tags(model, events, all_tags, tag_embeddings)
    
    # Print results
    for event in processed_events:
        print(f"\nEvent: {event['title']}")
        print(f"Main Categories: {event.get('main_categories', [])}")
        print(f"Event Types: {event.get('event_types', [])}")
        print(f"Academic Topics: {event.get('academic_topics', [])}")
        print(f"Predicted Tags: {event.get('assigned_tags', [])}")
    
    return processed_events

if __name__ == "__main__":
    test_assign_event_tags()
