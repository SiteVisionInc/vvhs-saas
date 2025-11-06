"""
Volunteer schemas for profile management.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from models.volunteer import VolunteerStatus, AccountStatus, MRCLevel


class VolunteerBase(BaseModel):
    """Base volunteer schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    
    # Contact
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: str = "VA"
    zip_code: Optional[str] = None
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class VolunteerCreate(VolunteerBase):
    """Schema for creating volunteer."""
    password: str = Field(..., min_length=8)
    tenant_id: int
    mrc_level: MRCLevel = MRCLevel.LEVEL_1


class VolunteerUpdate(BaseModel):
    """Schema for updating volunteer."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    application_status: Optional[VolunteerStatus] = None
    account_status: Optional[AccountStatus] = None
    mrc_level: Optional[MRCLevel] = None


class VolunteerResponse(VolunteerBase):
    """Schema for volunteer response."""
    id: int
    tenant_id: int
    application_status: VolunteerStatus
    account_status: AccountStatus
    mrc_level: MRCLevel
    total_hours: int
    alert_response_rate: int
    application_date: datetime
    approval_date: Optional[datetime]
    last_activity_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class VolunteerListResponse(BaseModel):
    """Schema for volunteer list response."""
    total: int
    items: list[VolunteerResponse]


class VolunteerStatsResponse(BaseModel):
    """Dashboard statistics for volunteers."""
    total_volunteers: int
    approved_volunteers: int
    pending_applications: int
    incomplete_applications: int
    working_volunteers: int
