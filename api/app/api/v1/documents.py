# api/app/api/v1/documents.py
"""
Document management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, date, timedelta

from database import get_db
from models.user import User
from models.volunteer import Volunteer
from models.document import (
    PolicyDocument,
    ElectronicSignature,
    VolunteerDocument,
    DocumentAccessLog
)
from api.deps import get_current_user
from schemas.document import (
    PolicyDocumentCreate,
    PolicyDocumentUpdate,
    PolicyDocumentResponse,
    ElectronicSignatureCreate,
    ElectronicSignatureResponse,
    VolunteerDocumentCreate,
    VolunteerDocumentUpdate,
    VolunteerDocumentResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    ExpiringDocumentReport,
    SignatureLogResponse,
    DocumentAccessLogCreate
)
from services.s3_storage import s3_storage

router = APIRouter()


# =============== Policy Documents ===============

@router.get("/policies", response_model=List[PolicyDocumentResponse])
def list_policy_documents(
    active_only: bool = True,
    requires_signature: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List organizational policy documents."""
    query = db.query(PolicyDocument).filter(
        PolicyDocument.tenant_id == current_user.tenant_id
    )
    
    if active_only:
        query = query.filter(PolicyDocument.is_active == True)
    
    if requires_signature is not None:
        query = query.filter(PolicyDocument.requires_signature == requires_signature)
    
    policies = query.order_by(PolicyDocument.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        PolicyDocumentResponse(
            **policy.__dict__,
            is_expired=policy.is_expired
        )
        for policy in policies
    ]


@router.post("/policies", response_model=PolicyDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_policy_document(
    policy_data: PolicyDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new policy document (admin only)."""
    # Check permissions
    if current_user.role not in ["system_admin", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create policy documents"
        )
    
    # Create policy
    policy = PolicyDocument(
        **policy_data.dict(),
        created_by=current_user.id
    )
    
    db.add(policy)
    db.commit()
    db.refresh(policy)
    
    return PolicyDocumentResponse(
        **policy.__dict__,
        is_expired=policy.is_expired
    )


@router.get("/policies/{policy_id}", response_model=PolicyDocumentResponse)
def get_policy_document(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific policy document."""
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id,
        PolicyDocument.tenant_id == current_user.tenant_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    # Log access
    log_document_access(
        db=db,
        document_id=policy_id,
        document_type="policy_document",
        action="view",
        user_id=current_user.id
    )
    
    return PolicyDocumentResponse(
        **policy.__dict__,
        is_expired=policy.is_expired
    )


# =============== Electronic Signatures ===============

@router.post("/sign", response_model=ElectronicSignatureResponse, status_code=status.HTTP_201_CREATED)
def sign_document(
    signature_data: ElectronicSignatureCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create an electronic signature for a document.
    Captures IP, user agent, and timestamp for non-repudiation.
    """
    # Get volunteer record if current user is a volunteer
    volunteer = db.query(Volunteer).filter(
        Volunteer.email == current_user.email,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    # Create signature
    signature = ElectronicSignature(
        volunteer_id=volunteer.id if volunteer else None,
        user_id=current_user.id if not volunteer else None,
        policy_document_id=signature_data.policy_document_id,
        custom_document_id=signature_data.custom_document_id,
        signature_data=signature_data.signature_data,
        signature_method=signature_data.signature_method,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        geolocation=signature_data.geolocation,
        consent_text=signature_data.consent_text,
        acknowledged_terms=signature_data.acknowledged_terms,
        timestamp=datetime.utcnow()
    )
    
    db.add(signature)
    db.commit()
    db.refresh(signature)
    
    # Log action
    log_document_access(
        db=db,
        document_id=signature_data.policy_document_id or signature_data.custom_document_id,
        document_type="policy_document" if signature_data.policy_document_id else "volunteer_document",
        action="sign",
        user_id=current_user.id,
        volunteer_id=volunteer.id if volunteer else None
    )
    
    return signature


@router.get("/policies/{policy_id}/signatures", response_model=SignatureLogResponse)
def get_policy_signatures(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all signatures for a policy document (admin only)."""
    if current_user.role not in ["system_admin", "org_admin", "coordinator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id,
        PolicyDocument.tenant_id == current_user.tenant_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Get all signatures
    signatures = db.query(ElectronicSignature).filter(
        ElectronicSignature.policy_document_id == policy_id
    ).all()
    
    # Find volunteers who haven't signed
    signed_volunteer_ids = {s.volunteer_id for s in signatures if s.volunteer_id}
    all_volunteers = db.query(Volunteer).filter(
        Volunteer.tenant_id == current_user.tenant_id,
        Volunteer.application_status == 'approved'
    ).all()
    
    unsigned_volunteers = [
        {"id": v.id, "name": v.full_name, "email": v.email}
        for v in all_volunteers
        if v.id not in signed_volunteer_ids
    ]
    
    return SignatureLogResponse(
        document_id=policy_id,
        document_title=policy.title,
        signatures=signatures,
        unsigned_volunteers=unsigned_volunteers
    )


# =============== Volunteer Documents ===============

@router.post("/upload-request", response_model=DocumentUploadResponse)
def request_document_upload(
    upload_request: DocumentUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request a presigned URL for uploading a document to S3.
    Creates the database record and returns upload URL.
    """
    # Verify volunteer access
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == upload_request.volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Check if user has permission to upload for this volunteer
    if current_user.role == 'volunteer':
        # Volunteers can only upload for themselves
        if volunteer.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot upload documents for other volunteers"
            )
    
    # Generate S3 presigned URL
    try:
        upload_url, s3_key = s3_storage.generate_upload_url(
            file_name=upload_request.file_name,
            file_type=upload_request.file_type,
            tenant_id=current_user.tenant_id,
            document_type=upload_request.document_type,
            expires_in=3600  # 1 hour
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )
    
    # Create document record
    document = VolunteerDocument(
        volunteer_id=upload_request.volunteer_id,
        tenant_id=current_user.tenant_id,
        document_type=upload_request.document_type,
        title=upload_request.file_name,
        file_url=f"s3://{s3_storage.bucket_name}/{s3_key}",
        file_name=upload_request.file_name,
        file_size_bytes=upload_request.file_size_bytes,
        file_type=upload_request.file_type,
        uploaded_by=current_user.id,
        verification_status='pending'
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return DocumentUploadResponse(
        upload_url=upload_url,
        document_id=document.id,
        expires_in=3600
    )


@router.get("/volunteers/{volunteer_id}/documents", response_model=List[VolunteerDocumentResponse])
def list_volunteer_documents(
    volunteer_id: int,
    document_type: Optional[str] = None,
    include_expired: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all documents for a volunteer."""
    # Verify access
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    query = db.query(VolunteerDocument).filter(
        VolunteerDocument.volunteer_id == volunteer_id
    )
    
    if document_type:
        query = query.filter(VolunteerDocument.document_type == document_type)
    
    if not include_expired:
        query = query.filter(
            or_(
                VolunteerDocument.expires == False,
                VolunteerDocument.expiration_date >= date.today()
            )
        )
    
    documents = query.order_by(VolunteerDocument.uploaded_at.desc()).all()
    
    return [
        VolunteerDocumentResponse(
            **doc.__dict__,
            is_expired=doc.is_expired,
            days_until_expiration=doc.days_until_expiration
        )
        for doc in documents
    ]


@router.patch("/documents/{document_id}/verify", response_model=VolunteerDocumentResponse)
def verify_document(
    document_id: int,
    verification: VolunteerDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify or reject a volunteer document (coordinator only)."""
    if current_user.role not in ["system_admin", "org_admin", "coordinator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    document = db.query(VolunteerDocument).filter(
        VolunteerDocument.id == document_id,
        VolunteerDocument.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update verification status
    if verification.verification_status:
        document.verification_status = verification.verification_status
        document.verified_by = current_user.id
        document.verified_at = datetime.utcnow()
    
    if verification.rejection_reason:
        document.rejection_reason = verification.rejection_reason
    
    db.commit()
    db.refresh(document)
    
    return VolunteerDocumentResponse(
        **document.__dict__,
        is_expired=document.is_expired,
        days_until_expiration=document.days_until_expiration
    )


@router.get("/expiring", response_model=List[ExpiringDocumentReport])
def get_expiring_documents(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get report of documents expiring within X days."""
    cutoff_date = date.today() + timedelta(days=days)
    
    documents = db.query(
        VolunteerDocument,
        Volunteer
    ).join(
        Volunteer, VolunteerDocument.volunteer_id == Volunteer.id
    ).filter(
        Volunteer.tenant_id == current_user.tenant_id,
        VolunteerDocument.expires == True,
        VolunteerDocument.expiration_date.isnot(None),
        VolunteerDocument.expiration_date <= cutoff_date,
        VolunteerDocument.expiration_date >= date.today()
    ).order_by(
        VolunteerDocument.expiration_date
    ).all()
    
    results = []
    for doc, volunteer in documents:
        days_remaining = (doc.expiration_date - date.today()).days
        results.append(ExpiringDocumentReport(
            volunteer_id=volunteer.id,
            volunteer_name=volunteer.full_name,
            document_type=doc.document_type,
            document_title=doc.title,
            expiration_date=doc.expiration_date,
            days_until_expiration=days_remaining
        ))
    
    return results


# =============== Helper Functions ===============

def log_document_access(
    db: Session,
    document_id: int,
    document_type: str,
    action: str,
    user_id: Optional[int] = None,
    volunteer_id: Optional[int] = None,
    meta_data: Optional[dict] = None
):
    """Log document access for audit trail."""
    log_entry = DocumentAccessLog(
        document_id=document_id,
        document_type=document_type,
        action=action,
        user_id=user_id,
        volunteer_id=volunteer_id,
        meta_data=meta_data
    )
    db.add(log_entry)
    db.commit()
