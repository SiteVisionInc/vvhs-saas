"""
Behavioral Health Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ==================== PATIENT SCHEMAS ====================

class BHPatientBase(BaseModel):
    """Base patient schema."""
    mrn: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    dob: Optional[date] = None
    gender: Optional[str] = None
    guardians: Optional[List[Dict[str, Any]]] = None
    addresses: Optional[List[Dict[str, Any]]] = None
    phones: Optional[List[Dict[str, Any]]] = None
    emergency_contacts: Optional[List[Dict[str, Any]]] = None
    consent_flags: Optional[Dict[str, bool]] = None
    risk_level: str = "low"
    notes: Optional[str] = None


class BHPatientCreate(BHPatientBase):
    """Schema for creating a patient."""
    tenant_id: int


class BHPatientUpdate(BaseModel):
    """Schema for updating patient."""
    mrn: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    guardians: Optional[List[Dict[str, Any]]] = None
    addresses: Optional[List[Dict[str, Any]]] = None
    phones: Optional[List[Dict[str, Any]]] = None
    emergency_contacts: Optional[List[Dict[str, Any]]] = None
    consent_flags: Optional[Dict[str, bool]] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None


class BHPatientResponse(BHPatientBase):
    """Schema for patient response."""
    id: int
    tenant_id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SCREENING SCHEMAS ====================

class BHScreeningBase(BaseModel):
    """Base screening schema."""
    instrument_type: str = Field(..., description="C-SSRS, ASAM, PHQ-9, etc.")
    score: Optional[Decimal] = None
    details_json: Optional[Dict[str, Any]] = None
    screening_date: datetime = Field(default_factory=datetime.utcnow)


class BHScreeningCreate(BHScreeningBase):
    """Schema for creating screening."""
    patient_id: int
    clinician_id: int


class BHScreeningResponse(BHScreeningBase):
    """Schema for screening response."""
    id: int
    patient_id: int
    clinician_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== FACILITY SCHEMAS ====================

class BHFacilityBase(BaseModel):
    """Base facility schema."""
    name: str = Field(..., min_length=1, max_length=255)
    facility_type: str
    region_id: Optional[int] = None
    capabilities: Optional[List[str]] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    address: Optional[Dict[str, str]] = None
    emr_id: Optional[str] = None
    is_active: bool = True


class BHFacilityCreate(BHFacilityBase):
    """Schema for creating facility."""
    tenant_id: int


class BHFacilityUpdate(BaseModel):
    """Schema for updating facility."""
    name: Optional[str] = None
    facility_type: Optional[str] = None
    region_id: Optional[int] = None
    capabilities: Optional[List[str]] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    address: Optional[Dict[str, str]] = None
    emr_id: Optional[str] = None
    is_active: Optional[bool] = None


class BHFacilityResponse(BHFacilityBase):
    """Schema for facility response."""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== BED SNAPSHOT SCHEMAS ====================

class BHBedSnapshotBase(BaseModel):
    """Base bed snapshot schema."""
    unit_name: Optional[str] = None
    bed_type: str
    capacity_total: int = Field(..., ge=0)
    capacity_available: int = Field(..., ge=0)
    constraints: Optional[Dict[str, Any]] = None


class BHBedSnapshotCreate(BHBedSnapshotBase):
    """Schema for creating/updating bed snapshot."""
    facility_id: int
    reported_by: Optional[int] = None


class BHBedSnapshotResponse(BHBedSnapshotBase):
    """Schema for bed snapshot response."""
    id: int
    facility_id: int
    last_reported_at: datetime
    reported_by: Optional[int] = None
    is_stale: bool
    
    class Config:
        from_attributes = True


class BedSearchRequest(BaseModel):
    """Request schema for bed availability search."""
    facility_type: Optional[str] = None
    bed_type: Optional[str] = None
    region_id: Optional[int] = None
    min_available: int = 1
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    capabilities: Optional[List[str]] = None
    distance_miles: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BedSearchResult(BaseModel):
    """Result schema for bed search."""
    facility_id: int
    facility_name: str
    facility_type: str
    bed_type: str
    available_beds: int
    total_beds: int
    distance_miles: Optional[float] = None
    contact_phone: Optional[str] = None
    last_updated: datetime
    is_stale: bool
    
    class Config:
        from_attributes = True


# ==================== REFERRAL SCHEMAS ====================

class BHReferralBase(BaseModel):
    """Base referral schema."""
    region_id: Optional[int] = None
    priority: str = "routine"
    notes: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class BHReferralCreate(BHReferralBase):
    """Schema for creating referral."""
    patient_id: int


class BHReferralUpdate(BaseModel):
    """Schema for updating referral."""
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    placement_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None


class BHReferralResponse(BHReferralBase):
    """Schema for referral response."""
    id: int
    patient_id: int
    created_by: int
    status: str
    referral_date: datetime
    placement_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BHReferralDetailResponse(BHReferralResponse):
    """Detailed referral with patient and placement info."""
    patient: BHPatientResponse
    placements: List["BHPlacementResponse"] = []
    
    class Config:
        from_attributes = True


# ==================== PLACEMENT SCHEMAS ====================

class BHPlacementBase(BaseModel):
    """Base placement schema."""
    bed_type: str
    transport_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class BHPlacementCreate(BHPlacementBase):
    """Schema for creating placement."""
    referral_id: int
    facility_id: int


class BHPlacementUpdate(BaseModel):
    """Schema for updating placement."""
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    transport_details: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = None
    length_of_stay: Optional[int] = None
    notes: Optional[str] = None


class BHPlacementResponse(BHPlacementBase):
    """Schema for placement response."""
    id: int
    referral_id: int
    facility_id: int
    decision_by: int
    decision_date: datetime
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    outcome: Optional[str] = None
    length_of_stay: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AcceptReferralRequest(BaseModel):
    """Request to accept a referral and create placement."""
    bed_type: str
    admission_date: Optional[datetime] = None
    transport_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class DeclineReferralRequest(BaseModel):
    """Request to decline a referral."""
    reason_code: str
    reason_notes: Optional[str] = None


# ==================== FOLLOW-UP SCHEMAS ====================

class BHFollowUpBase(BaseModel):
    """Base follow-up schema."""
    scheduled_date: date
    followup_type: str = "day_30"
    notes: Optional[str] = None


class BHFollowUpCreate(BHFollowUpBase):
    """Schema for creating follow-up."""
    placement_id: int
    assigned_to: Optional[int] = None


class BHFollowUpUpdate(BaseModel):
    """Schema for updating follow-up."""
    completed_date: Optional[date] = None
    outcome_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class BHFollowUpResponse(BHFollowUpBase):
    """Schema for follow-up response."""
    id: int
[O    placement_id: int
    assigned_to: Optional[int] = None
    completed_date: Optional[date] = None
    completed_by: Optional[int] = None
    outcome_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CONSENT SCHEMAS ====================

class ElectronicConsentCapture(BaseModel):
    """Schema for capturing electronic consent."""
    patient_id: int
    consent_type: str  # treatment, release_info, research
    consent_text: str
    signature_data: str  # Base64 encoded signature
    ip_address: str
    user_agent: Optional[str] = None
    consented: bool = True


class ConsentResponse(BaseModel):
    """Response after consent capture."""
    patient_id: int
    consent_type: str
    consented: bool
    captured_at: datetime
    
    class Config:
        from_attributes = True


# ==================== DOCUMENT UPLOAD SCHEMAS ====================

class DocumentUploadRequest(BaseModel):
    """Request for document upload URL."""
    referral_id: int
    document_type: str  # treatment_history, assessment, other
    file_name: str
    file_size_bytes: int
    file_type: str


class DocumentUploadResponse(BaseModel):
    """Response with presigned upload URL."""
    upload_url: str
    document_id: str
    expires_at: datetime


# ==================== STATISTICS/REPORTING SCHEMAS ====================

class BHStatisticsResponse(BaseModel):
    """BH module statistics for dashboard."""
    total_patients: int
    total_referrals: int
    pending_referrals: int
    active_placements: int
    avg_placement_time_hours: Optional[float] = None
    bed_utilization_rate: Optional[float] = None
    
    # By status
    referrals_by_status: Dict[str, int]
    
    # By facility type
    placements_by_facility_type: Dict[str, int]
    
    class Config:
        from_attributes = True


class StaleBedsAlert(BaseModel):
    """Alert for facilities with stale bed data."""
    facility_id: int
    facility_name: str
    last_updated: datetime
    hours_stale: float
    contact_phone: Optional[str] = None


# Update forward references
BHReferralDetailResponse.model_rebuild()
