from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, date
import json

from database import get_db, Event
from models import EventList, Institution, InstitutionList

router = APIRouter()

@router.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NYC Academic Events API",
        "version": "1.0.0",
        "endpoints": {
            "events": "/api/events",
            "event_by_id": "/api/events/{event_id}",
            "institutions": "/api/institutions",
            "docs": "/docs"
        }
    }

@router.get("/api/events", response_model=EventList)
async def get_events(
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of events to return"),
    institution: Optional[str] = Query(None, description="Filter by institution (e.g., 'columbia', 'nyu')"),
    source_group: Optional[str] = Query(None, description="Filter by source group (e.g., 'columbia_classics', 'nyu_stern')"),
    date_from: Optional[str] = Query(None, description="Filter events from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter events to date (YYYY-MM-DD)"),
    academic_only: bool = Query(True, description="Return only academic events"),
    db: Session = Depends(get_db)
):
    """Get academic events with optional filtering"""
    query = db.query(Event)
    
    if academic_only:
        query = query.filter(Event.is_academic == True)
    
    if institution:
        query = query.filter(Event.source == institution)
    
    if source_group:
        query = query.filter(Event.source_group == source_group)
    
    if date_from:
        query = query.filter(Event.start_date >= date_from)
    
    if date_to:
        query = query.filter(Event.start_date <= date_to)
    
    total = query.count()
    events = query.order_by(Event.start_date.asc()).offset(skip).limit(limit).all()
    
    return EventList(
        events=events,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@router.get("/api/events/{event_id}", response_model=Event)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get a specific event by ID"""
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/api/institutions", response_model=InstitutionList)
async def get_institutions(db: Session = Depends(get_db)):
    """Get list of institutions with event counts"""
    institutions = db.query(
        Event.source_name,
        Event.source_group,
        func.count(Event.id).label('event_count')
    ).filter(Event.is_academic == True).group_by(
        Event.source_name, Event.source_group
    ).order_by(desc('event_count')).all()
    
    institution_list = [
        Institution(
            name=inst.source_name or inst.source_group,
            source_group=inst.source_group,
            event_count=inst.event_count
        )
        for inst in institutions
    ]
    
    return InstitutionList(
        institutions=institution_list,
        total=len(institution_list)
    )

@router.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get API statistics"""
    total_events = db.query(Event).filter(Event.is_academic == True).count()
    total_institutions = db.query(Event.source_group).filter(Event.is_academic == True).distinct().count()
    
    # Get events by month
    monthly_stats = db.query(
        func.substr(Event.start_date, 1, 7).label('month'),
        func.count(Event.id).label('count')
    ).filter(
        Event.is_academic == True,
        Event.start_date.isnot(None)
    ).group_by('month').order_by('month').all()
    
    return {
        "total_academic_events": total_events,
        "total_institutions": total_institutions,
        "monthly_events": [
            {"month": stat.month, "count": stat.count}
            for stat in monthly_stats
        ],
        "last_updated": datetime.now().isoformat()
    }
