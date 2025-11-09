"""
Behavioral Health API endpoints - Patient Management.
Handles patient intake, screening, and consent workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.user import User
from models.behavioral_health import (
    BHPatient, BHScreening, BHUser
)
from schemas.behavioral_health import (
    BHPatientCreate, BHPatientUpdate, BHPatientResponse,
    BHScreeningCreate, BHScreeningResponse,
    ElectronicConsentCapture, ConsentResponse
)
from api.deps import get_current_user
from services.audit import log_action

router = APIRouter()


# ==================== PATIENT CRUD ====================

@router.post("/", response_model=BHPatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_data: BHPatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new behavioral health patient.
    Clinician creates patient profile during intake.
    """
    # Create patient
    patient = BHPatient(
        **patient_data.dict(exclude={'tenant_id'}),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id
    )
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    # Audit log
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_patient.created",
        resource_type="bh_patient",
        resource_id=patient.id,
        description=f"Created BH patient: {patient.first_name} {patient.last_name}",
        new_values=patient_data.dict()
    )
    
    return patient


@router.get("/{patient_id}", response_model=BHPatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient by ID."""
    patient = db.query(BHPatient).filter(
        BHPatient.id == patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return patient


@router.put("/{patient_id}", response_model=BHPatientResponse)
def update_patient(
    patient_id: int,
    patient_data: BHPatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update patient information."""
    patient = db.query(BHPatient).filter(
        BHPatient.id == patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Store old values for audit
    old_values = {
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "risk_level": patient.risk_level
    }
    
    # Update fields
    for field, value in patient_data.dict(exclude_unset=True).items():
        setattr(patient, field, value)
    
    patient.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(patient)
    
    # Audit log
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_patient.updated",
        resource_type="bh_patient",
        resource_id=patient.id,
        description=f"Updated BH patient: {patient.first_name} {patient.last_name}",
        old_values=old_values,
        new_values=patient_data.dict(exclude_unset=True)
    )
    
    return patient


@router.get("/", response_model=List[BHPatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all patients with optional filtering."""
    query = db.query(BHPatient).filter(
        BHPatient.tenant_id == current_user.tenant_id
    )
    
    if risk_level:
        query = query.filter(BHPatient.risk_level == risk_level)
    
    patients = query.offset(skip).limit(limit).all()
    return patients


# ==================== SCREENING ====================

@router.post("/screenings", response_model=BHScreeningResponse, status_code=status.HTTP_201_CREATED)
def create_screening(
    screening_data: BHScreeningCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a clinical screening/assessment.
    Supports C-SSRS, ASAM, PHQ-9, etc.
    """
    # Verify patient exists
    patient = db.query(BHPatient).filter(
        BHPatient.id == screening_data.patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create screening
    screening = BHScreening(**screening_data.dict())
    
    db.add(screening)
    db.commit()
    db.refresh(screening)
    
    # Update patient risk level based on screening
    # (This would be more sophisticated in production)
    if screening.instrument_type == "C-SSRS" and screening.score and screening.score >= 4:
        patient.risk_level = "high"
    elif screening.instrument_type == "PHQ-9" and screening.score and screening.score >= 15:
        patient.risk_level = "medium"
    
    db.commit()
    
    # Audit log
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_screening.created",
        resource_type="bh_screening",
        resource_id=screening.id,
        description=f"Screening {screening.instrument_type} for patient {patient.id}",
        new_values=screening_data.dict()
    )
    
    return screening


@router.get("/{patient_id}/screenings", response_model=List[BHScreeningResponse])
def get_patient_screenings(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all screenings for a patient."""
    # Verify patient exists and belongs to tenant
    patient = db.query(BHPatient).filter(
        BHPatient.id == patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    screenings = db.query(BHScreening).filter(
        BHScreening.patient_id == patient_id
    ).order_by(BHScreening.screening_date.desc()).all()
    
    return screenings


# ==================== CONSENT MANAGEMENT ====================

@router.post("/{patient_id}/consent", response_model=ConsentResponse)
def capture_consent(
    patient_id: int,
    consent_data: ElectronicConsentCapture,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Capture electronic consent from patient or guardian.
    Implements non-repudiation requirements.
    """
    # Verify patient
    patient = db.query(BHPatient).filter(
        BHPatient.id == patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update consent flags
    if not patient.consent_flags:
        patient.consent_flags = {}
    
    patient.consent_flags[consent_data.consent_type] = consent_data.consented
    
    db.commit()
    
    # Audit log with full consent capture details
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_consent.captured",
        resource_type="bh_patient",
        resource_id=patient.id,
        description=f"Consent captured: {consent_data.consent_type}",
        new_values={
            "consent_type": consent_data.consent_type,
            "consented": consent_data.consented,
            "ip_address": consent_data.ip_address,
            "user_agent": consent_data.user_agent,
            "consent_text": consent_data.consent_text[:200]  # Truncate for audit
        },
        ip_address=consent_data.ip_address,
        user_agent=consent_data.user_agent
    )
    
    return ConsentResponse(
        patient_id=patient.id,
        consent_type=consent_data.consent_type,
        consented=consent_data.consented,
        captured_at=datetime.utcnow()
    )


@router.get("/{patient_id}/consents")
def get_patient_consents(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all consent flags for a patient."""
    patient = db.query(BHPatient).filter(
        BHPatient.id == patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return {
        "patient_id": patient.id,
        "consents": patient.consent_flags or {}
    }


# ==================== DOCUMENT UPLOAD ====================

@router.post("/{patient_id}/documents/upload-request")
async def request_document_upload(
    patient_id: int,
    document_type: str,
    file_name: str,
    file_size_bytes: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request a presigned URL for document upload.
    Documents stored in S3 and linked to patient.
    """
    # Verify patient
    patient = db.query(BHPatient).filter(
        BHPatient.id == patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # TODO: Generate presigned S3 URL
    # This is a placeholder - implement with boto3
    
    return {
        "upload_url": f"https://s3.amazonaws.com/bh-documents/patient-{patient_id}/{file_name}",
        "document_id": f"doc-{patient_id}-{int(datetime.utcnow().timestamp())}",
        "expires_at": datetime.utcnow().isoformat()
    }
