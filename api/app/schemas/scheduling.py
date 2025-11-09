"""
Schemas for advanced scheduling features.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum


class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class WaitlistStatus(str, Enum):
    WAITING = "waiting"
    PROMOTED = "promoted"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SwapRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class AvailabilityType(str, Enum):
    GENERAL = "general"
    SPECIFIC_EVENT = "specific_event"
    BLACKOUT = "blackout"


# Shift Template Schemas
class RecurrencePattern(BaseModel):
    frequency: RecurrenceFrequency
    days: List[int]  # 0=Sunday, 1=Monday, etc.
    interval: int = 1  # Every X weeks/months
    until: Optional[date] = None


class ShiftTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    duration_minutes: int = Field(..., gt=0)
    max_volunteers: Optional[int] = Field(None, gt=0)
    min_volunteers: int = Field(1, gt=0)
    required_skills: Optional[List[str]] = None
    required_training: Optional[List[str]] = None
    allow_self_signup: bool = False
    enable_waitlist: bool = True


class ShiftTemplateCreate(ShiftTemplateBase):
    tenant_id: int


class ShiftTemplateResponse(ShiftTemplateBase):
    id: int
    tenant_id: int
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Waitlist Schemas
class WaitlistJoinRequest(BaseModel):
    shift_id: int
    notes: Optional[str] = None
    auto_accept: bool = False


class WaitlistResponse(BaseModel):
    id: int
    shift_id: int
    volunteer_id: int
    position: int
    priority_score: int
    status: WaitlistStatus
    joined_at: datetime
    promoted_at: Optional[datetime]
    notified_at: Optional[datetime]
    notes: Optional[str]
    
    # Include volunteer info
    volunteer_name: Optional[str] = None
    volunteer_email: Optional[str] = None
    
    class Config:
        from_attributes = True


# Availability Schemas
class AvailabilityBase(BaseModel):
    start_date: date
    end_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    availability_type: AvailabilityType = AvailabilityType.GENERAL
    event_id: Optional[int] = None
    notes: Optional[str] = None


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class AvailabilityResponse(AvailabilityBase):
    id: int
    volunteer_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Shift Swap Schemas
class SwapRequestCreate(BaseModel):
    original_assignment_id: int
    target_volunteer_id: Optional[int] = None
    reason: Optional[str] = None


class SwapRequestResponse(BaseModel):
    id: int
    original_assignment_id: int
    requesting_volunteer_id: int
    target_volunteer_id: Optional[int]
    status: SwapRequestStatus
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    reason: Optional[str]
    created_at: datetime
    
    # Include details
    shift_name: Optional[str] = None
    shift_date: Optional[datetime] = None
    requesting_volunteer_name: Optional[str] = None
    target_volunteer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Enhanced Shift Schemas
class ShiftSelfSignupRequest(BaseModel):
    shift_id: int
    notes: Optional[str] = None


class AvailableShiftResponse(BaseModel):
    id: int
    event_id: int
    name: str
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    max_volunteers: Optional[int]
    current_volunteers: int
    available_spots: int
    waitlist_count: int
    allow_self_signup: bool
    enable_waitlist: bool
    required_skills: Optional[List[str]]
    
    # Event details
    event_name: str
    event_description: Optional[str]
    
    class Config:
        from_attributes = True


# Bulk Operations
class BulkShiftCreateRequest(BaseModel):
    template_id: int
    event_id: int
    start_date: date
    end_date: date
    location: Optional[str] = None


class BulkShiftCreateResponse(BaseModel):
    created_count: int
    shifts_created: List[int]
    message: str