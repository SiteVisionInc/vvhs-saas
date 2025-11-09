# api/app/schemas/time_tracking.py
"""
Time tracking schemas.
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============ Time Entries ============

class TimeEntryBase(BaseModel):
    event_id: Optional[int] = None
    shift_id: Optional[int] = None
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    volunteer_notes: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    volunteer_id: int
    entry_method: str = 'manual'
    
    # Optional geolocation
    check_in_lat: Optional[Decimal] = None
    check_in_lng: Optional[Decimal] = None
    check_out_lat: Optional[Decimal] = None
    check_out_lng: Optional[Decimal] = None


class TimeEntryBulkCreate(BaseModel):
    """Bulk time entry for multiple volunteers."""
    event_id: Optional[int] = None
    entries: list[dict]  # [{volunteer_id, check_in_time, check_out_time, notes}]


class TimeEntryUpdate(BaseModel):
    check_out_time: Optional[datetime] = None
    coordinator_notes: Optional[str] = None
    status: Optional[str] = None
    rejection_reason: Optional[str] = None


class TimeEntryResponse(BaseModel):
    id: int
    tenant_id: int
    volunteer_id: int
    event_id: Optional[int]
    shift_id: Optional[int]
    check_in_time: datetime
    check_out_time: Optional[datetime]
    duration_minutes: Optional[int]
    hours_decimal: Optional[float]
    entry_method: str
    status: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    volunteer_notes: Optional[str]
    coordinator_notes: Optional[str]
    created_at: datetime
    
    # Include volunteer details
    volunteer_name: Optional[str] = None
    event_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class TimeEntryApproval(BaseModel):
    """Approve or reject time entry."""
    status: str  # approved, rejected
    coordinator_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    hours_override: Optional[Decimal] = None  # Allow coordinator to adjust hours


class BulkTimeEntryApproval(BaseModel):
    """Bulk approve/reject multiple entries."""
    entry_ids: list[int]
    action: str  # approve, reject
    notes: Optional[str] = None


# ============ QR Codes ============

class QRCodeCreate(BaseModel):
    event_id: Optional[int] = None
    shift_id: Optional[int] = None
    valid_from: datetime
    valid_until: datetime
    max_uses: Optional[int] = None
    require_photo: bool = False
    require_signature: bool = False
    allow_early_checkin_minutes: int = 15
    allow_late_checkout_minutes: int = 30


class QRCodeResponse(BaseModel):
    id: int
    event_id: Optional[int]
    shift_id: Optional[int]
    qr_code_hash: str
    qr_code_url: str
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    use_count: int
    max_uses: Optional[int]
    created_at: datetime
    
    # Include event details
    event_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============ Check-in ============

class CheckinRequest(BaseModel):
    """Volunteer check-in via QR code or kiosk."""
    qr_code_hash: Optional[str] = None
    volunteer_id: Optional[int] = None
    event_id: Optional[int] = None
    device_info: Optional[dict] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


class CheckoutRequest(BaseModel):
    """Volunteer check-out."""
    session_id: Optional[int] = None
    time_entry_id: Optional[int] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    notes: Optional[str] = None


class CheckinResponse(BaseModel):
    """Response after check-in."""
    success: bool
    message: str
    session_id: Optional[int] = None
    time_entry_id: Optional[int] = None
    volunteer_name: str
    event_name: Optional[str] = None
    check_in_time: datetime


# ============ Reports ============

class VolunteerHoursReport(BaseModel):
    """Volunteer hours summary."""
    volunteer_id: int
    volunteer_name: str
    total_hours: float
    approved_hours: float
    pending_hours: float
    entry_count: int
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]


class PendingApprovalsReport(BaseModel):
    """Summary of pending hour approvals."""
    total_pending: int
    total_hours_pending: float
    oldest_entry_date: Optional[datetime]
    entries: list[TimeEntryResponse]