"""
Event filtering module for academic event scrapers.
This module provides functions to filter out unwanted events before they are saved.
"""

import re
from datetime import datetime, timezone

def should_filter_event(event):
    """
    Determine if an event should be filtered out based on various criteria.
    
    Args:
        event (dict): The event dictionary containing at least 'name' and 'description' keys
        
    Returns:
        bool: True if the event should be filtered out, False if it should be kept
    """
    if not event:
        return True
    
    # Get event name and description, defaulting to empty strings
    name = event.get('name', '').lower()
    description = event.get('description', '').lower()
    
    # Combine name and description for comprehensive filtering
    event_text = f"{name} {description}"
    
    # Filter out events with these terms in the title or description
    filter_terms = [
        # Virtual/Online training and basic courses
        'virtual naloxone training',
        'naloxone training',
        'office hours',
        'office hour',
        'virtual office hours',
        'online office hours',
        
        # Fairs and expos (comprehensive list)
        'fair',
        'expo',
        'exposition',
        'career fair',
        'job fair',
        'internship fair',
        'graduate school fair',
        'fellowship fair',
        'research fair',
        'science fair',
        'art fair',
        'book fair',
        'health fair',
        'wellness fair',
        'information fair',
        'resource fair',
        'opportunity fair',
        'recruitment fair',
        'admissions fair',
        'transfer fair',
        'study abroad fair',
        'international fair',
        
        # Basic/Introductory courses
        '101',
        'intro ',
        'introduction ',
        'introductory ',
        'beginner',
        'beginners',
        'basic ',
        'basics ',
        'elementary ',
        'fundamental ',
        'prerequisite ',
        'survey course',
        
        # Faculty/Staff specific events
        '(for faculty)',
        'for faculty',
        'faculty only',
        'staff only',
        'employee only',
        'internal only',
        'faculty meeting',
        'staff meeting',
        'department meeting',
        'committee meeting',
        'board meeting',
        'administrative meeting',
        
        # Administrative/Technical systems
        'courseworks',
        'courseworks ',
        'canvas',
        'blackboard',
        'moodle',
        'brightspace',
        'learning management',
        'lms training',
        'system training',
        'software training',
        
        # Medical/Clinical rounds
        'grand rounds',
        'grand round',
        'clinical rounds',
        'medical rounds',
        'hospital rounds',
        'patient rounds',
        
        # Basic workshops and training
        'basic workshop',
        'basic training',
        'intro workshop',
        'intro training',
        'elementary workshop',
        'fundamental workshop',
        'prerequisite workshop',
        
        # Basic seminars and lectures (be more specific)
        'intro seminar',
        'basic seminar', 
        '101 seminar',
        'introductory seminar',
        'intro lecture',
        'basic lecture',
        '101 lecture',
        'elementary lecture',
        'fundamental lecture',
        
        # Student services (basic/administrative)
        'student orientation',
        'new student',
        'transfer student',
        'international student orientation',
        'academic advising',
        'registration help',
        'financial aid workshop',
        'bursar office',
        'registrar office',
        
        # Administrative events
        'open house',
        'information session',
        'info session',
        'drop-in',
        'walk-in',
        'appointment',
        'consultation',
        'advising session',
        
        # Basic academic events
        'study group',
        'tutoring',
        'review session',
        'make-up class',
        'makeup class',
        'extra help',
        'office hours',
        'help session',
    ]
    
    # Check if any filter terms are present
    for term in filter_terms:
        if term in event_text:
            # Debug output removed for production
            return True
    
    # Additional regex patterns for more complex filtering
    filter_patterns = [
        r'\b101\b',  # Standalone "101" (not part of larger numbers)
        # Removed overly aggressive course number filter that was catching room numbers
        r'\(for faculty\)',  # Exact match for faculty-specific events
        r'\bteaching\b.*\b101\b',  # Teaching + 101 combination
        r'\bintro\b.*\bworkshop\b',  # Intro + workshop combination
        r'\bfair\b.*\b(fellowship|career|job|internship|admission|recruitment|transfer|study\s+abroad)\b',  # Specific types of fairs
        r'\b(office\s+hours?|drop.?in|walk.?in)\b',  # Office hours variations
        r'\b(basic|intro|elementary|fundamental)\b.*\b(training|workshop|seminar|lecture)\b',  # Basic academic events
        r'\b(orientation|information\s+session|info\s+session)\b',  # Orientation and info sessions
        r'\b(study\s+group|tutoring|review\s+session|extra\s+help)\b',  # Basic academic support
        r'\b(make.?up\s+class|makeup\s+class)\b',  # Make-up classes
        r'\b(prerequisite|survey\s+course)\b',  # Prerequisites and survey courses
        r'\b(learning\s+management|lms|system\s+training|software\s+training)\b',  # Technical training
    ]
    
    
    for pattern in filter_patterns:
        if re.search(pattern, event_text, re.IGNORECASE):
            return True
    
    # Filter out events that are too short (likely incomplete or spam)
    if len(name.strip()) < 5:
        return True
    
    # Filter out events that are just dates or times
    if re.match(r'^\d{1,2}:\d{2}\s*(am|pm)?$', name.strip()):
        return True
    
    # Filter out events that are just dates
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', name.strip()):
        return True
    
    # Filter out events that are just room numbers or building names
    if re.match(r'^(room|rm\.?)\s*\d+', name.strip()):
        return True
    
    # Filter out events that are just building names
    if re.match(r'^(building|hall|center|library|lab|laboratory)\s*\d*$', name.strip(), re.IGNORECASE):
        return True
    
    # Filter out events that are too generic or administrative
    generic_terms = [
        'meeting', 'session', 'event', 'activity', 'program', 'workshop',
        'lecture', 'presentation', 'discussion', 'conversation', 'talk', 'speech'
    ]
    
    # If the title is just a generic term, filter it out
    if name.strip().lower() in generic_terms:
        return True
    
    # Filter out Columbia Information Session events specifically
    if should_filter_columbia_info_sessions(event):
        return True
    
    # Filter out events that have already occurred
    if should_filter_by_date(event):
        return True
    
    return False

def should_filter_columbia_info_sessions(event):
    """
    Filter out Columbia Information Session events specifically.
    These events have "Information Session" in their tags or audience fields.
    
    Args:
        event (dict): The event dictionary
        
    Returns:
        bool: True if the event should be filtered out, False if it should be kept
    """
    # Check if this is a Columbia event
    source_name = event.get('metadata', {}).get('source_name', '').lower()
    if 'columbia' not in source_name:
        return False
    
    # Check tags for "Information Session"
    tags = event.get('metadata', {}).get('additional_info', {}).get('tags', [])
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and 'information session' in tag.lower():
                return True
    
    # Check audience for "Information Session"
    audience = event.get('metadata', {}).get('additional_info', {}).get('audience', [])
    if isinstance(audience, list):
        for aud in audience:
            if isinstance(aud, str) and 'information session' in aud.lower():
                return True
    
    # Check event_type for "Information Session"
    event_type = event.get('metadata', {}).get('additional_info', {}).get('event_type', '')
    if isinstance(event_type, str) and 'information session' in event_type.lower():
        return True
    
    return False

def should_filter_by_date(event):
    """
    Determine if an event should be filtered out based on its date.
    
    Args:
        event (dict): The event dictionary containing start_date and end_date
        
    Returns:
        bool: True if the event should be filtered out (past event), False if it should be kept
    """
    # Get current time in UTC
    now = datetime.now(timezone.utc)
    
    # Check start date first
    start_date = event.get('start_date')
    if start_date:
        try:
            # Try to parse the start date
            if isinstance(start_date, str):
                # Handle ISO format strings
                if 'T' in start_date:
                    # ISO format with time: "2024-01-15T14:30:00Z"
                    parsed_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                else:
                    # Date only: "2024-01-15" - assume start of day
                    parsed_start = datetime.fromisoformat(start_date + 'T00:00:00+00:00')
            else:
                # Already a datetime object
                parsed_start = start_date
            
            # If start date is in the past, filter it out
            if parsed_start < now:
                return True
                
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse start_date '{start_date}': {e}")
            # If we can't parse the date, keep the event to be safe
            pass
    
    # Check end date as fallback
    end_date = event.get('end_date')
    if end_date and not start_date:
        try:
            # Try to parse the end date
            if isinstance(end_date, str):
                # Handle ISO format strings
                if 'T' in end_date:
                    # ISO format with time: "2024-01-15T14:30:00Z"
                    parsed_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    # Date only: "2024-01-15" - assume end of day
                    parsed_end = datetime.fromisoformat(end_date + 'T23:59:59+00:00')
            else:
                # Already a datetime object
                parsed_end = end_date
            
            # If end date is in the past, filter it out
            if parsed_end < now:
                return True
                
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse end_date '{end_date}': {e}")
            # If we can't parse the date, keep the event to be safe
            pass
    
    # If no valid dates found, keep the event to be safe
    return False

def filter_events(events_list):
    """
    Filter a list of events using the should_filter_event function.
    
    Args:
        events_list (list): List of event dictionaries
        
    Returns:
        list: Filtered list of events
    """
    if not events_list:
        return []
    
    original_count = len(events_list)
    filtered_events = []
    
    for event in events_list:
        if not should_filter_event(event):
            filtered_events.append(event)
    
    filtered_count = len(filtered_events)
    removed_count = original_count - filtered_count
    
    if removed_count > 0:
        print(f"Filtered out {removed_count} events ({original_count} -> {filtered_count})")
    
    return filtered_events

def get_filter_stats(original_events, filtered_events):
    """
    Get statistics about the filtering process.
    
    Args:
        original_events (list): Original list of events
        filtered_events (list): Filtered list of events
        
    Returns:
        dict: Statistics about the filtering
    """
    original_count = len(original_events) if original_events else 0
    filtered_count = len(filtered_events) if filtered_events else 0
    removed_count = original_count - filtered_count
    
    return {
        'original_count': original_count,
        'filtered_count': filtered_count,
        'removed_count': removed_count,
        'removal_percentage': (removed_count / original_count * 100) if original_count > 0 else 0
    }
