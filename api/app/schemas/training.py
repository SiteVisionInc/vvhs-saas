# api/app/schemas/training.py
"""
Training and certification schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


# ============ Training Courses ============

class TrainingCourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    course_code: Optional[str] = None
    provider: Optional[str] = None
    category: Optional[str] = None
    is_required: bool = False
    validity_period_days: Optional[int] = None


class TrainingCourseCreate(TrainingCourseBase):
    tenant_id: int
    train_course_id: Optional[str] = None


class TrainingCourseResponse(TrainingCourseBase):
    id: int
    tenant_id: int
    train_course_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Volunteer Training ============

class VolunteerTrainingBase(BaseModel):
    course_id: int
    completion_date: date
    expiration_date: Optional[date] = None
    score: Optional[Decimal] = None
    certificate_number: Optional[str] = None


class VolunteerTrainingCreate(VolunteerTrainingBase):
    volunteer_id: int
    certificate_url: Optional[str] = None


class VolunteerTrainingResponse(VolunteerTrainingBase):
    id: int
    volunteer_id: int
    status: str
    train_completion_id: Optional[str]
    synced_from_train: bool
    is_expired: bool
    created_at: datetime
    
    # Include course details
    course_name: Optional[str] = None
    course_provider: Optional[str] = None
    course_category: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============ Certifications ============

class CertificationBase(BaseModel):
    certification_type: str
    license_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    notes: Optional[str] = None


class CertificationCreate(CertificationBase):
    volunteer_id: int
    document_url: Optional[str] = None


class CertificationUpdate(BaseModel):
    expiration_date: Optional[date] = None
    verification_status: Optional[str] = None
    notes: Optional[str] = None


class CertificationResponse(CertificationBase):
    id: int
    volunteer_id: int
    verification_status: str
    verification_date: Optional[date]
    is_expired: bool
    days_until_expiration: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Training Status ============

class TrainingStatusSummary(BaseModel):
    """Summary of volunteer's training status."""
    volunteer_id: int
    total_courses: int
    completed_courses: int
    expired_courses: int
    expiring_soon: int  # Within 90 days
    compliance_percentage: float
    missing_required: list[str]


class ExpiringTrainingReport(BaseModel):
    """Report of expiring training."""
    volunteer_id: int
    volunteer_name: str
    course_name: str
    expiration_date: date
    days_until_expiration: int
    is_required: bool


# ============ TRAIN Sync ============

class TRAINSyncRequest(BaseModel):
    """Request to sync training from TRAIN."""
    volunteer_id: Optional[int] = None  # If None, sync all
    force: bool = False  # Force re-sync


class TRAINSyncResponse(BaseModel):
    """Response from TRAIN sync."""
    success: bool
    records_synced: int
    errors: list[str]
    message: str