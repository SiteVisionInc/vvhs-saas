"""
Event schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.event import ActivityType, EventStatus

class EventBase(BaseModel):
    """Base event schema."""
    name: str = Field(..., min_length=1, max_length=255)
    staff_description: Optional[str] = None
    volunteer_description: Optional[str] = None
    location: Optional[str] = None
    locality: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    activity_type: ActivityType
    visible_to_volunteers: bool = True
    allow_self_signup: bool = False

class EventCreate(EventBase):
    """Schema for creating an event."""
    tenant_id: int
    response_name: Optional[str] = None
    requestor_type: Optional[str] = None

class EventUpdate(BaseModel):
    """Schema for updating event."""
    name: Optional[str] = None
    staff_description: Optional[str] = None
    volunteer_description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    visible_to_volunteers: Optional[bool] = None
    status: Optional[EventStatus] = None

class EventResponse(EventBase):
    """Schema for event response."""
    id: int
    tenant_id: int
    status: EventStatus
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    # Computed fields for frontend compatibility
    title: str = None  # Will be populated from 'name'
    event_date: str = None  # Will be populated from 'start_date'
    max_volunteers: Optional[int] = None
    registered_volunteers: int = 0
    
    class Config:
        from_attributes = True
        
    def __init__(self, **data):
        super().__init__(**data)
        # Map backend fields to frontend expectations
        self.title = data.get('name', '')
        if data.get('start_date'):
            self.event_date = data['start_date'].isoformat()

class EventListResponse(BaseModel):
    """Schema for event list response."""
    total: int
    items: List[EventResponse]

# For frontend compatibility - simplified response
class EventSimpleResponse(BaseModel):
    """Simplified event response matching frontend expectations exactly."""
    id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    event_date: str
    location: Optional[str] = None
    max_volunteers: Optional[int] = None
    registered_volunteers: int = 0
    created_by: str