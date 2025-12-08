#!/usr/bin/env python3
"""
Standardized Date Utilities for Academic Event Scrapers
Ensures consistent date formatting across all scrapers
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import re
from typing import Optional, Tuple, Union

NY_TZ = ZoneInfo("America/New_York")

def standardize_datetime(dt: Optional[Union[datetime, str]]) -> Optional[str]:
    """
    Convert any datetime object or string to standardized ISO format in NYC timezone.
    
    ALL EVENT TIMES ARE STORED IN NYC TIMEZONE (America/New_York).
    This ensures consistent display and prevents timezone confusion.
    
    Args:
        dt: datetime object, ISO string, or None
        
    Returns:
        ISO 8601 formatted string in NYC timezone (America/New_York) or None if invalid
        
    Examples:
        >>> standardize_datetime(datetime(2025, 9, 3, 14, 0))
        '2025-09-03T14:00:00-04:00'  # or -05:00 depending on DST
        
        >>> standardize_datetime('2025-09-03T14:00:00')
        '2025-09-03T14:00:00-04:00'
        
        >>> standardize_datetime(None)
        None
    """
    if dt is None:
        return None
    
    # If it's already a string, try to parse it
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return None
    
    # Ensure it's a datetime object
    if not isinstance(dt, datetime):
        return None
    
    # Make timezone-aware if it isn't already
    if dt.tzinfo is None:
        # Assume naive datetimes are in NYC time
        dt = dt.replace(tzinfo=NY_TZ)
    else:
        # Convert to NYC timezone if it has a different timezone
        dt = dt.astimezone(NY_TZ)
    
    # Return ISO format with NYC timezone
    return dt.isoformat()

def parse_flexible_date(date_str: str, time_str: str = "", default_hour: int = 9) -> Optional[datetime]:
    """
    Parse various date formats into a datetime object in NYC timezone.
    
    Args:
        date_str: Date string in various formats
        time_str: Time string (optional)
        default_hour: Default hour if no time specified
        
    Returns:
        datetime object in NYC timezone (America/New_York) or None if parsing fails
        
    Supported date formats:
        - "September 3, 2025"
        - "Sep 3, 2025" 
        - "9/3/2025"
        - "2025-09-03"
        - "September 3" (assumes current year)
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    current_year = datetime.now(NY_TZ).year
    
    try:
        dt = None
        # Format 1: "September 3, 2025"
        if re.match(r'^[A-Z][a-z]+ \d{1,2}, \d{4}$', date_str):
            dt = datetime.strptime(date_str, "%B %d, %Y")
        
        # Format 2: "Sep 3, 2025" 
        elif re.match(r'^[A-Z][a-z]{2,3}\.?\s+\d{1,2}, \d{4}$', date_str):
            # Handle abbreviated months
            date_str = date_str.replace('.', '')
            dt = datetime.strptime(date_str, "%b %d, %Y")
        
        # Format 3: "9/3/2025"
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
            dt = datetime.strptime(date_str, "%m/%d/%Y")
        
        # Format 4: "2025-09-03"
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Format 5: "September 3" (assume current year)
        elif re.match(r'^[A-Z][a-z]+ \d{1,2}$', date_str):
            date_str = f"{date_str}, {current_year}"
            dt = datetime.strptime(date_str, "%B %d, %Y")
        
        # Format 6: "Sep 3" (assume current year)
        elif re.match(r'^[A-Z][a-z]{2,3}\.?\s+\d{1,2}$', date_str):
            date_str = f"{date_str}, {current_year}"
            date_str = date_str.replace('.', '')
            dt = datetime.strptime(date_str, "%b %d, %Y")
        
        # Format 7: "3 September 2025" (European format)
        elif re.match(r'^\d{1,2} [A-Z][a-z]+ \d{4}$', date_str):
            dt = datetime.strptime(date_str, "%d %B %Y")
        
        # Format 8: "3 Sep 2025" (European abbreviated)
        elif re.match(r'^\d{1,2} [A-Z][a-z]{2,3}\.?\s+\d{4}$', date_str):
            date_str = date_str.replace('.', '')
            dt = datetime.strptime(date_str, "%d %b %Y")
        
        # Attach NYC timezone to all parsed dates
        if dt is not None:
            return dt.replace(tzinfo=NY_TZ)
        
    except ValueError:
        pass
    
    return None

def parse_flexible_time(time_str: str) -> Optional[datetime.time]:
    """
    Parse various time formats into a time object.
    
    Args:
        time_str: Time string in various formats
        
    Returns:
        time object or None if parsing fails
        
    Supported time formats:
        - "2:00 PM"
        - "14:00"
        - "2 PM"
        - "14:00:00"
    """
    if not time_str:
        return None
    
    time_str = time_str.strip()
    
    try:
        # Format 1: "2:00 PM" or "2:00 PM"
        if re.match(r'^\d{1,2}:\d{2}\s*(AM|PM)$', time_str, re.IGNORECASE):
            return datetime.strptime(time_str, "%I:%M %p").time()
        
        # Format 2: "2 PM" or "2 AM"
        elif re.match(r'^\d{1,2}\s*(AM|PM)$', time_str, re.IGNORECASE):
            return datetime.strptime(time_str, "%I %p").time()
        
        # Format 3: "14:00" (24-hour)
        elif re.match(r'^\d{1,2}:\d{2}$', time_str):
            return datetime.strptime(time_str, "%H:%M").time()
        
        # Format 4: "14:00:00" (24-hour with seconds)
        elif re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):
            return datetime.strptime(time_str, "%H:%M:%S").time()
        
    except ValueError:
        pass
    
    return None

def create_event_dates(date_str: str, time_str: str = "", duration_hours: int = 2) -> Tuple[Optional[str], Optional[str]]:
    """
    Create standardized start and end dates for an event in NYC timezone.
    
    Args:
        date_str: Date string
        time_str: Time string (optional)
        duration_hours: Default duration if no end time specified
        
    Returns:
        Tuple of (start_date_iso, end_date_iso) strings in NYC timezone
    """
    # Parse the date (already in NYC timezone)
    date_obj = parse_flexible_date(date_str)
    if not date_obj:
        return None, None
    
    # Parse the time if provided
    time_obj = parse_flexible_time(time_str)
    
    # Create start datetime in NYC timezone
    if time_obj:
        start_datetime = datetime.combine(date_obj.date(), time_obj, tzinfo=NY_TZ)
    else:
        # Default to 9 AM if no time specified
        start_datetime = datetime.combine(date_obj.date(), datetime.min.time().replace(hour=9), tzinfo=NY_TZ)
    
    # Create end datetime
    if time_str and ("–" in time_str or "-" in time_str):
        # Parse end time from range like "2:00 PM – 5:00 PM"
        time_parts = re.split(r'[–\-]', time_str)
        if len(time_parts) == 2:
            end_time = parse_flexible_time(time_parts[1].strip())
            if end_time:
                end_datetime = datetime.combine(date_obj.date(), end_time, tzinfo=NY_TZ)
            else:
                end_datetime = start_datetime + timedelta(hours=duration_hours)
        else:
            end_datetime = start_datetime + timedelta(hours=duration_hours)
    else:
        # Use default duration
        end_datetime = start_datetime + timedelta(hours=duration_hours)
    
    # Standardize both dates (already in NYC timezone, just format)
    start_iso = standardize_datetime(start_datetime)
    end_iso = standardize_datetime(end_datetime)
    
    return start_iso, end_iso

def create_multi_day_event_dates(start_date_str: str, end_date_str: str, time_str: str = "") -> Tuple[Optional[str], Optional[str]]:
    """
    Create standardized start and end dates for multi-day events in NYC timezone.
    
    Args:
        start_date_str: Start date string
        end_date_str: End date string  
        time_str: Time string (optional)
        
    Returns:
        Tuple of (start_date_iso, end_date_iso) strings in NYC timezone
    """
    # Parse start date (already in NYC timezone)
    start_date_obj = parse_flexible_date(start_date_str)
    if not start_date_obj:
        return None, None
    
    # Parse end date (already in NYC timezone)
    end_date_obj = parse_flexible_date(end_date_str)
    if not end_date_obj:
        return None, None
    
    # Parse time if provided
    time_obj = parse_flexible_time(time_str)
    
    # Create start datetime in NYC timezone
    if time_obj:
        start_datetime = datetime.combine(start_date_obj.date(), time_obj, tzinfo=NY_TZ)
    else:
        start_datetime = datetime.combine(start_date_obj.date(), datetime.min.time().replace(hour=9), tzinfo=NY_TZ)
    
    # Create end datetime (end of day if no specific time)
    if time_obj:
        end_datetime = datetime.combine(end_date_obj.date(), time_obj, tzinfo=NY_TZ)
    else:
        end_datetime = datetime.combine(end_date_obj.date(), datetime.min.time().replace(hour=23, minute=59), tzinfo=NY_TZ)
    
    # Standardize both dates (already in NYC timezone, just format)
    start_iso = standardize_datetime(start_datetime)
    end_iso = standardize_datetime(end_datetime)
    
    return start_iso, end_iso

def is_future_event(start_date: str) -> bool:
    """
    Check if an event is in the future.
    
    Args:
        start_date: ISO formatted date string
        
    Returns:
        True if event is in the future, False otherwise
    """
    try:
        event_date = datetime.fromisoformat(start_date)
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)
        else:
            event_date = event_date.astimezone(timezone.utc)
        
        now = datetime.now(timezone.utc)
        return event_date > now
        
    except (ValueError, TypeError):
        return False

def format_display_date(iso_date: str) -> str:
    """
    Convert ISO date to human-readable format for display in NYC time.
    
    Args:
        iso_date: ISO formatted date string (should already be in NYC timezone)
        
    Returns:
        Human-readable date string like "September 3, 2025 at 2:00 PM" (NYC time)
    """
    try:
        dt = datetime.fromisoformat(iso_date)
        
        # Ensure it's in NYC timezone
        if dt.tzinfo is None:
            # If naive, assume it's NYC time
            dt = dt.replace(tzinfo=NY_TZ)
        else:
            # Convert to NYC timezone if it's in a different timezone
            dt = dt.astimezone(NY_TZ)

        # Format: "September 3, 2025 at 2:00 PM" (NYC local time)
        # Use platform-specific format codes
        try:
            # Unix-style (works on Linux/Mac)
            return dt.strftime("%B %-d, %Y at %-I:%M %p")
        except ValueError:
            # Windows-style fallback
            return dt.strftime("%B %d, %Y at %I:%M %p").replace(" 0", " ")
        
    except (ValueError, TypeError):
        return iso_date

def create_nyc_datetime(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
    """
    Create a datetime object in NYC timezone.
    
    This is the recommended way for scrapers to create datetime objects.
    All event times should be in NYC timezone.
    
    Args:
        year, month, day: Date components
        hour, minute, second: Time components (default to midnight)
        
    Returns:
        datetime object in NYC timezone (America/New_York)
        
    Example:
        >>> create_nyc_datetime(2025, 12, 3, 19, 0)
        datetime.datetime(2025, 12, 3, 19, 0, tzinfo=ZoneInfo('America/New_York'))
    """
    return datetime(year, month, day, hour, minute, second, tzinfo=NY_TZ)

def to_nyc_datetime(dt: Union[datetime, str]) -> Optional[datetime]:
    """
    Convert any datetime or ISO string to NYC timezone.
    
    Args:
        dt: datetime object or ISO string
        
    Returns:
        datetime object in NYC timezone, or None if invalid
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return None
    
    if not isinstance(dt, datetime):
        return None
    
    if dt.tzinfo is None:
        # Assume naive datetimes are in NYC time
        return dt.replace(tzinfo=NY_TZ)
    else:
        # Convert to NYC timezone
        return dt.astimezone(NY_TZ)

# Convenience functions for common use cases
def quick_date(date_str: str, time_str: str = "") -> Optional[str]:
    """Quick way to get a standardized date string in NYC timezone."""
    start_date, _ = create_event_dates(date_str, time_str)
    return start_date

def quick_datetime_range(start_date_str: str, end_date_str: str, time_str: str = "") -> Tuple[Optional[str], Optional[str]]:
    """Quick way to get standardized start and end dates for multi-day events in NYC timezone."""
    return create_multi_day_event_dates(start_date_str, end_date_str, time_str)



