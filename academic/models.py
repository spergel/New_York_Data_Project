from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    source: str
    source_group: str
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    venue_name: Optional[str] = None
    venue_type: Optional[str] = None

    class Config:
        orm_mode = True

class EventCreate(EventBase):
    event_id: str

class Event(EventBase):
    id: int
    event_id: str
    is_academic: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EventList(BaseModel):
    events: List[Event]
    total: int
    page: int
    per_page: int

class Institution(BaseModel):
    name: str
    source_group: str
    event_count: int

class InstitutionList(BaseModel):
    institutions: List[Institution]
    total: int
