"""
Models for the NYC Events scraper.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Union

class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"
    RESCHEDULED = "rescheduled"

class EventCategory(str, Enum):
    # General Categories
    TECH = "tech"
    BUSINESS = "business"
    ARTS = "arts"
    CULTURE = "culture"
    EDUCATION = "education"
    SCIENCE = "science"
    HEALTH = "health"
    EXERCISE = "exercise"
    SOCIAL = "social"
    NETWORKING = "networking"
    OTHER = "other"
    
    # Academic Categories
    LECTURES = "lectures_seminars"
    CONFERENCES = "conferences_symposia"
    WORKSHOPS = "workshops_trainings"
    PANELS = "panel_discussions"
    RESEARCH = "research_presentations"
    PERFORMANCES = "performances_exhibitions"
    STUDENT = "student_activities"
    CEREMONIES = "academic_ceremonies"
    
    # Tech Categories
    TECH_TALKS = "tech_talks"
    HACKATHONS = "hackathons_competitions"
    NETWORKING_SOCIAL = "networking_social"
    TECH_WORKSHOPS = "workshops_training"
    STARTUP = "startup_entrepreneurship"
    INNOVATION = "tech_innovation"
    COWORKING = "coworking_workspace"
    SPECIAL_INTEREST = "special_interest"
    
    # Exercise Categories
    FITNESS = "fitness"
    SPORTS = "sports"
    YOGA = "yoga"
    MEDITATION = "meditation"
    DANCE = "dance"
    MARTIAL_ARTS = "martial_arts"
    OUTDOOR = "outdoor"
    WELLNESS = "wellness"
    
    # Additional Common Categories
    COMMUNITY = "community"
    FOOD = "food"
    MUSIC = "music"
    FILM = "film"
    THEATER = "theater"
    LITERATURE = "literature"
    POLITICS = "politics"
    ENVIRONMENT = "environment"
    CHARITY = "charity"
    FAMILY = "family"
    PROFESSIONAL = "professional"
    CAREER = "career"
    LANGUAGE = "language"
    GAMES = "games"
    FASHION = "fashion"
    PHOTOGRAPHY = "photography"
    DESIGN = "design"
    CRAFTS = "crafts"


@dataclass
class Price:
    amount: float
    type: str  # "free", "paid", "donation"
    details: Optional[str] = None

@dataclass
class Venue:
    name: str
    address: Optional[str] = None
    type: str = "venue"

@dataclass
class Organizer:
    name: str
    type: str = "organizer"

@dataclass
class EventMetadata:
    source_url: str
    source_name: str
    venue: Optional[Venue] = None
    organizer: Optional[Organizer] = None
    additional_info: Optional[Dict] = None
    raw_data: Optional[Dict] = None

@dataclass
class Event:
    id: str
    name: str
    type: str
    location_id: Optional[str]
    community_id: Optional[str]
    description: str
    start_date: datetime
    end_date: datetime
    category: Union[EventCategory, List[EventCategory]]
    price: Price
    status: EventStatus = EventStatus.SCHEDULED
    registration_required: bool = False
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    metadata: Optional[EventMetadata] = None

@dataclass
class SubstackPost:
    """Model for Substack newsletter posts."""
    id: str
    title: str
    subtitle: Optional[str]
    publication: str
    url: str
    post_date: datetime
    description: str
    cover_image: Optional[str]
    excerpt: Optional[str]
    type: str = "substack"
    metadata: Optional[Dict] = None 