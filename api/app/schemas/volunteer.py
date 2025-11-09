"""
Volunteer schemas for profile management.
FIXED: Proper field types matching the database DECIMAL fields.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


# Add this new schema for public registration
class PublicVolunteerRegistration(BaseModel):
    """Public volunteer self-registration schema - no authentication required"""
    # Tenant selection
    tenant_id: int
    
    # Step 1: Basic Information
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_primary: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: str = "VA"
    zip_code: Optional[str] = None
    
    # Step 2: Emergency Contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    
    # Step 3: Skills and Availability
    skills: Optional[str] = None
    languages: Optional[str] = None
    availability: Optional[str] = None
    occupation: Optional[str] = None
    
    # Password
    password: str = Field(..., min_length=8)


class RegistrationSuccessResponse(BaseModel):
    """Response after successful registration"""
    message: str
    volunteer_id: int
    email: str
    status: str


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
    mrc_level: Optional[str] = None


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
    
    application_status: Optional[str] = None
    account_status: Optional[str] = None
    mrc_level: Optional[str] = None


class VolunteerResponse(BaseModel):
    """Schema for volunteer response - matches actual DB fields with proper types."""
    id: int
    tenant_id: int
    username: str
    email: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    
    # Contact
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Emergency Contact  
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    
    # Status fields - all optional
    application_status: Optional[str] = None
    account_status: Optional[str] = None
    mrc_level: Optional[str] = None  # This must be optional
    
    # Professional Information
    occupation: Optional[str] = None
    employer: Optional[str] = None
    professional_skills: Optional[str] = None
    license_number: Optional[str] = None
    license_type: Optional[str] = None
    license_state: Optional[str] = None
    license_expiration: Optional[date] = None
    
    # Skills and Languages
    skills: Optional[str] = None
    languages: Optional[str] = None
    
    # Training
    certifications: Optional[str] = None
    certification_info: Optional[str] = None
    train_id: Optional[str] = None
    train_data: Optional[str] = None
    
    # Availability
    availability: Optional[str] = None
    availability_info: Optional[str] = None
    travel_distance: Optional[int] = None
    preferred_roles: Optional[str] = None
    assigned_groups: Optional[str] = None
    assigned_roles: Optional[str] = None
    
    # Metrics - DECIMAL fields in DB, so use float/Decimal
    total_hours: Optional[float] = 0  # Changed from int to float
    alert_response_rate: Optional[float] = 0  # Changed from int to float
    badges_earned: Optional[str] = None
    
    # Background Check
    background_check_date: Optional[date] = None
    background_check_status: Optional[str] = None
    
    # Important Dates
    application_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    
    # System Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    
    # Computed properties for frontend compatibility
    @property
    def status(self) -> str:
        return self.application_status or "unknown"
    
    @property
    def phone(self) -> Optional[str]:
        return self.phone_primary
    
    @property
    def hours_completed(self) -> float:
        return self.total_hours or 0
    
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