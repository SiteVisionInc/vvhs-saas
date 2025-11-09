# api/app/schemas/document.py
"""
Pydantic schemas for document management.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""
    PHOTO_ID = "photo_id"
    DRIVERS_LICENSE = "drivers_license"
    PROFESSIONAL_LICENSE = "professional_license"
    CERTIFICATION = "certification"
    INSURANCE = "insurance"
    WAIVER = "waiver"
    POLICY = "policy"
    OTHER = "other"


class SignatureMethod(str, Enum):
    """Signature capture method."""
    DRAWN = "drawn"
    TYPED = "typed"
    CLICK_THROUGH = "click_through"
    BIOMETRIC = "biometric"


class VerificationStatus(str, Enum):
    """Document verification status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


# ============ Policy Documents ============

class PolicyDocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: str
    version: str
    requires_signature: bool = False
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None


class PolicyDocumentCreate(PolicyDocumentBase):
    tenant_id: int
    file_url: str
    file_size_bytes: Optional[int] = None
    file_hash: Optional[str] = None


class PolicyDocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    expiration_date: Optional[date] = None


class PolicyDocumentResponse(PolicyDocumentBase):
    id: int
    tenant_id: int
    file_url: str
    file_size_bytes: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_expired: bool
    
    class Config:
        from_attributes = True


# ============ Electronic Signatures ============

class ElectronicSignatureCreate(BaseModel):
    # What to sign
    policy_document_id: Optional[int] = None
    custom_document_id: Optional[int] = None
    
    # Signature data
    signature_data: Optional[str] = None  # Base64 encoded image
    signature_method: SignatureMethod
    
    # Consent
    consent_text: str
    acknowledged_terms: bool = True
    
    # Location (optional)
    geolocation: Optional[dict] = None
    
    @validator('policy_document_id', 'custom_document_id')
    def check_document_id(cls, v, values):
        """Ensure at least one document ID is provided."""
        if not v and not values.get('policy_document_id') and not values.get('custom_document_id'):
            raise ValueError('Must specify either policy_document_id or custom_document_id')
        return v


class ElectronicSignatureResponse(BaseModel):
    id: int
    volunteer_id: Optional[int]
    user_id: Optional[int]
    policy_document_id: Optional[int]
    custom_document_id: Optional[int]
    signature_method: str
    timestamp: datetime
    ip_address: str
    verified: bool
    
    class Config:
        from_attributes = True


# ============ Volunteer Documents ============

class VolunteerDocumentBase(BaseModel):
    document_type: DocumentType
    document_category: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    expires: bool = False


class VolunteerDocumentCreate(VolunteerDocumentBase):
    volunteer_id: int
    file_url: str
    file_name: str
    file_size_bytes: int
    file_type: str
    file_hash: Optional[str] = None


class VolunteerDocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    expiration_date: Optional[date] = None
    verification_status: Optional[VerificationStatus] = None
    rejection_reason: Optional[str] = None


class VolunteerDocumentResponse(VolunteerDocumentBase):
    id: int
    volunteer_id: int
    tenant_id: int
    file_url: str
    file_name: str
    file_size_bytes: int
    file_type: str
    verification_status: str
    verified_at: Optional[datetime]
    uploaded_at: datetime
    is_expired: bool
    days_until_expiration: int
    download_count: int
    
    class Config:
        from_attributes = True


# ============ Document Access ============

class DocumentAccessLogCreate(BaseModel):
    document_id: int
    document_type: str  # 'policy_document' or 'volunteer_document'
    action: str  # view, download, upload, delete, sign
    meta_data: Optional[dict] = None


# ============ Reports ============

class ExpiringDocumentReport(BaseModel):
    """Report of documents expiring soon."""
    volunteer_id: int
    volunteer_name: str
    document_type: str
    document_title: str
    expiration_date: date
    days_until_expiration: int


class SignatureLogResponse(BaseModel):
    """Signature history for a document."""
    document_id: int
    document_title: str
    signatures: List[ElectronicSignatureResponse]
    unsigned_volunteers: List[dict]  # Volunteers who need to sign


# ============ File Upload ============

class DocumentUploadRequest(BaseModel):
    """Request for S3 presigned URL."""
    volunteer_id: int
    document_type: DocumentType
    file_name: str
    file_size_bytes: int
    file_type: str


class DocumentUploadResponse(BaseModel):
    """Response with presigned URL for upload."""
    upload_url: str
    document_id: int
    expires_in: int  # Seconds
