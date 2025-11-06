"""Event management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models.user import User
from models.event import Event, EventAssignment, AssignmentStatus
from api.deps import get_current_user
from schemas.event import (
    EventResponse, 
    EventSimpleResponse, 
    EventListResponse,
    EventCreate,
    EventUpdate
)

router = APIRouter()

@router.get("/", response_model=List[EventSimpleResponse])
def list_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List events for the current tenant.
    Returns a simplified structure for frontend compatibility.
    """
    # Query events for current tenant
    events = db.query(Event).filter(
        Event.tenant_id == current_user.tenant_id,
        Event.visible_to_volunteers == True  # Only visible events
    ).offset(skip).limit(limit).all()
    
    # Transform to match frontend expectations
    result = []
    for event in events:
        # Count registered volunteers for this event
        registered_count = db.query(func.count(EventAssignment.id)).filter(
            EventAssignment.event_id == event.id,
            EventAssignment.status.in_([
                AssignmentStatus.CONFIRMED,
                AssignmentStatus.PENDING
            ])
        ).scalar() or 0
        
        # Calculate max volunteers from shifts
        max_volunteers = 0
        if event.shifts:
            max_volunteers = sum(shift.slots_total for shift in event.shifts)
        
        result.append(EventSimpleResponse(
            id=str(event.id),
            tenant_id=str(event.tenant_id),
            title=event.name,  # Map 'name' to 'title'
            description=event.volunteer_description or event.staff_description,
            event_date=event.start_date.isoformat() if event.start_date else "",
            location=event.location,
            max_volunteers=max_volunteers or 50,  # Default if no shifts
            registered_volunteers=registered_count,
            created_by=str(event.created_by) if event.created_by else "1"
        ))
    
    return result

@router.get("/detailed", response_model=EventListResponse)
def list_events_detailed(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List events with full details.
    Uses proper response schema with all fields.
    """
    query = db.query(Event).filter(Event.tenant_id == current_user.tenant_id)
    
    total = query.count()
    events = query.offset(skip).limit(limit).all()
    
    # Convert to response schema
    event_responses = []
    for event in events:
        # Count volunteers
        registered = db.query(func.count(EventAssignment.id)).filter(
            EventAssignment.event_id == event.id,
            EventAssignment.status == AssignmentStatus.CONFIRMED
        ).scalar() or 0
        
        # Create response with computed fields
        response_data = {
            **event.__dict__,
            'title': event.name,
            'event_date': event.start_date.isoformat() if event.start_date else None,
            'max_volunteers': sum(s.slots_total for s in event.shifts) if event.shifts else 0,
            'registered_volunteers': registered
        }
        
        event_responses.append(EventResponse(**response_data))
    
    return EventListResponse(total=total, items=event_responses)

@router.get("/{event_id}", response_model=EventSimpleResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single event by ID."""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.tenant_id == current_user.tenant_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Count registered volunteers
    registered_count = db.query(func.count(EventAssignment.id)).filter(
        EventAssignment.event_id == event.id,
        EventAssignment.status == AssignmentStatus.CONFIRMED
    ).scalar() or 0
    
    return EventSimpleResponse(
        id=str(event.id),
        tenant_id=str(event.tenant_id),
        title=event.name,
        description=event.volunteer_description or event.staff_description,
        event_date=event.start_date.isoformat() if event.start_date else "",
        location=event.location,
        max_volunteers=sum(s.slots_total for s in event.shifts) if event.shifts else 50,
        registered_volunteers=registered_count,
        created_by=str(event.created_by) if event.created_by else "1"
    )

@router.post("/", response_model=EventSimpleResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new event."""
    # Ensure user can create events (check permissions)
    if current_user.role.value not in ["system_admin", "org_admin", "coordinator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create events"
        )
    
    # Create event
    event = Event(
        **event_data.dict(exclude={'tenant_id'}),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        status="draft"
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return EventSimpleResponse(
        id=str(event.id),
        tenant_id=str(event.tenant_id),
        title=event.name,
        description=event.volunteer_description or event.staff_description,
        event_date=event.start_date.isoformat() if event.start_date else "",
        location=event.location,
        max_volunteers=50,
        registered_volunteers=0,
        created_by=str(event.created_by)
    )