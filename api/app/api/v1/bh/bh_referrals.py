"""
Behavioral Health API endpoints - Referrals & Placements.
Handles the complete referral workflow from submission to discharge.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.behavioral_health import (
    BHReferral, BHPlacement, BHPatient, BHFacility, BHBedSnapshot, BHFollowUp
)
from schemas.behavioral_health import (
    BHReferralCreate, BHReferralUpdate, BHReferralResponse, BHReferralDetailResponse,
    BHPlacementCreate, BHPlacementUpdate, BHPlacementResponse,
    AcceptReferralRequest, DeclineReferralRequest,
    BHFollowUpCreate, BHFollowUpUpdate, BHFollowUpResponse
)
from api.deps import get_current_user
from services.audit import log_action

router = APIRouter()


# ==================== REFERRAL CRUD ====================

@router.post("/", response_model=BHReferralResponse, status_code=status.HTTP_201_CREATED)
def create_referral(
    referral_data: BHReferralCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new referral.
    Clinician creates referral packet after intake/screening.
    """
    # Verify patient exists
    patient = db.query(BHPatient).filter(
        BHPatient.id == referral_data.patient_id,
        BHPatient.tenant_id == current_user.tenant_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create referral
    referral = BHReferral(
        **referral_data.dict(),
        created_by=current_user.id,
        status="draft",
        referral_date=datetime.utcnow()
    )
    
    db.add(referral)
    db.commit()
    db.refresh(referral)
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_referral.created",
        resource_type="bh_referral",
        resource_id=referral.id,
        description=f"Created referral for patient {patient.id}",
        new_values=referral_data.dict()
    )
    
    return referral


@router.get("/{referral_id}", response_model=BHReferralDetailResponse)
def get_referral(
    referral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get referral with full details including patient and placements."""
    referral = db.query(BHReferral).filter(
        BHReferral.id == referral_id
    ).first()
    
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    
    # Verify access to patient's tenant
    patient = referral.patient
    if patient.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return referral


@router.put("/{referral_id}", response_model=BHReferralResponse)
def update_referral(
    referral_id: int,
    referral_data: BHReferralUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update referral information."""
    referral = db.query(BHReferral).filter(
        BHReferral.id == referral_id
    ).first()
    
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    
    # Verify access
    patient = referral.patient
    if patient.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    for field, value in referral_data.dict(exclude_unset=True).items():
        setattr(referral, field, value)
    
    referral.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(referral)
    
    return referral


@router.post("/{referral_id}/submit", response_model=BHReferralResponse)
def submit_referral(
    referral_id: int,
    facility_ids: List[int],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit referral to selected facilities.
    Changes status from draft → submitted and sends to facilities.
    """
    referral = db.query(BHReferral).filter(
        BHReferral.id == referral_id
    ).first()
    
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    
    # Verify patient access
    patient = referral.patient
    if patient.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if already submitted
    if referral.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referral already submitted"
        )
    
    # Update status
    referral.status = "submitted"
    referral.referral_date = datetime.utcnow()
    
    db.commit()
    db.refresh(referral)
    
    # TODO: Send notifications to facilities
    # background_tasks.add_task(send_referral_notifications, referral_id, facility_ids)
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_referral.submitted",
        resource_type="bh_referral",
        resource_id=referral.id,
        description=f"Submitted referral to {len(facility_ids)} facilities",
        new_values={"facility_ids": facility_ids}
    )
    
    return referral


@router.get("/", response_model=List[BHReferralResponse])
def list_referrals(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List referrals with optional filtering."""
    # Get all patients for tenant
    patient_ids = db.query(BHPatient.id).filter(
        BHPatient.tenant_id == current_user.tenant_id
    ).all()
    patient_ids = [p[0] for p in patient_ids]
    
    query = db.query(BHReferral).filter(
        BHReferral.patient_id.in_(patient_ids)
    )
    
    if status:
        query = query.filter(BHReferral.status == status)
    
    if priority:
        query = query.filter(BHReferral.priority == priority)
    
    referrals = query.order_by(
        BHReferral.referral_date.desc()
    ).offset(skip).limit(limit).all()
    
    return referrals


# ==================== PLACEMENT MANAGEMENT ====================

@router.post("/{referral_id}/accept", response_model=BHPlacementResponse)
def accept_referral(
    referral_id: int,
    accept_data: AcceptReferralRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Facility coordinator accepts referral and creates placement.
    Updates referral status to 'accepted'.
    """
    referral = db.query(BHReferral).filter(
        BHReferral.id == referral_id
    ).first()
    
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    
    if referral.status not in ["submitted", "declined"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept referral with status: {referral.status}"
        )
    
    # Create placement
    placement = BHPlacement(
        referral_id=referral.id,
        facility_id=current_user.tenant_id,  # Assumes facility coordinator's tenant is facility
        bed_type=accept_data.bed_type,
        decision_by=current_user.id,
        decision_date=datetime.utcnow(),
        admission_date=accept_data.admission_date,
        transport_details=accept_data.transport_details,
        notes=accept_data.notes
    )
    
    # Update referral status
    referral.status = "accepted"
    referral.placement_date = datetime.utcnow()
    
    db.add(placement)
    db.commit()
    db.refresh(placement)
    
    # Update bed availability
    # TODO: Decrement available beds for facility
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_referral.accepted",
        resource_type="bh_placement",
        resource_id=placement.id,
        description=f"Accepted referral {referral.id}",
        new_values=accept_data.dict()
    )
    
    return placement


@router.post("/{referral_id}/decline")
def decline_referral(
    referral_id: int,
    decline_data: DeclineReferralRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Facility coordinator declines referral.
    Updates status and records reason.
    """
    referral = db.query(BHReferral).filter(
        BHReferral.id == referral_id
    ).first()
    
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    
    # Update status
    referral.status = "declined"
    
    # Add decline reason to notes
    decline_note = f"[DECLINED by {current_user.username} on {datetime.utcnow().isoformat()}]\n"
    decline_note += f"Reason: {decline_data.reason_code}\n"
    if decline_data.reason_notes:
        decline_note += f"Notes: {decline_data.reason_notes}\n"
    
    if referral.notes:
        referral.notes += "\n\n" + decline_note
    else:
        referral.notes = decline_note
    
    db.commit()
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_referral.declined",
        resource_type="bh_referral",
        resource_id=referral.id,
        description=f"Declined referral {referral.id}: {decline_data.reason_code}",
        new_values=decline_data.dict()
    )
    
    return {"status": "declined", "referral_id": referral.id}


@router.patch("/placements/{placement_id}/discharge", response_model=BHPlacementResponse)
def discharge_placement(
    placement_id: int,
    discharge_data: BHPlacementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record patient discharge from facility.
    Captures discharge details and outcomes.
    """
    placement = db.query(BHPlacement).filter(
        BHPlacement.id == placement_id
    ).first()
    
    if not placement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )
    
    # Update discharge fields
    placement.discharge_date = discharge_data.discharge_date or datetime.utcnow()
    placement.outcome = discharge_data.outcome
    
    # Calculate length of stay
    if placement.admission_date:
        los_delta = placement.discharge_date - placement.admission_date
        placement.length_of_stay = los_delta.days
    
    if discharge_data.notes:
        placement.notes = discharge_data.notes
    
    # Update referral status
    referral = placement.referral
    referral.status = "discharged"
    referral.discharge_date = placement.discharge_date
    
    db.commit()
    db.refresh(placement)
    
    # Create follow-up schedule
    # Schedule 30/60/90 day follow-ups
    for days, follow_type in [(30, "day_30"), (60, "day_60"), (90, "day_90")]:
        followup_date = placement.discharge_date + timedelta(days=days)
        
        followup = BHFollowUp(
            placement_id=placement.id,
            scheduled_date=followup_date.date(),
            followup_type=follow_type,
            status="scheduled"
        )
        db.add(followup)
    
    db.commit()
    
    # Update bed availability
    # TODO: Increment available beds for facility
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_placement.discharged",
        resource_type="bh_placement",
        resource_id=placement.id,
        description=f"Discharged placement {placement.id}: {placement.outcome}",
        new_values={
            "discharge_date": placement.discharge_date.isoformat(),
            "outcome": placement.outcome,
            "length_of_stay": placement.length_of_stay
        }
    )
    
    return placement


# ==================== FOLLOW-UP TRACKING ====================

@router.post("/placements/{placement_id}/followups", response_model=BHFollowUpResponse)
def create_followup(
    placement_id: int,
    followup_data: BHFollowUpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule a follow-up contact."""
    # Verify placement exists
    placement = db.query(BHPlacement).filter(
        BHPlacement.id == placement_id
    ).first()
    
    if not placement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )
    
    followup = BHFollowUp(**followup_data.dict())
    
    db.add(followup)
    db.commit()
    db.refresh(followup)
    
    return followup


@router.patch("/followups/{followup_id}/complete", response_model=BHFollowUpResponse)
def complete_followup(
    followup_id: int,
    followup_data: BHFollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record follow-up completion and outcome."""
    followup = db.query(BHFollowUp).filter(
        BHFollowUp.id == followup_id
    ).first()
    
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )
    
    # Update fields
    followup.completed_date = followup_data.completed_date or datetime.utcnow().date()
    followup.completed_by = current_user.id
    followup.outcome_data = followup_data.outcome_data
    followup.status = "completed"
    
    if followup_data.notes:
        followup.notes = followup_data.notes
    
    db.commit()
    db.refresh(followup)
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_followup.completed",
        resource_type="bh_followup",
        resource_id=followup.id,
        description=f"Completed {followup.followup_type} follow-up",
        new_values=followup_data.dict(exclude_unset=True)
    )
    
    return followup


@router.get("/followups/due", response_model=List[BHFollowUpResponse])
def get_due_followups(
    days_ahead: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get follow-ups due in the next N days."""
    end_date = datetime.utcnow().date() + timedelta(days=days_ahead)
    
    followups = db.query(BHFollowUp).filter(
        and_(
            BHFollowUp.status == "scheduled",
            BHFollowUp.scheduled_date <= end_date
        )
    ).order_by(BHFollowUp.scheduled_date).all()
    
    return followups
