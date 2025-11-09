"""Volunteer management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.user import User
from models.volunteer import Volunteer, VolunteerStatus
from api.deps import get_current_user
from schemas.volunteer import (
    VolunteerListResponse, 
    VolunteerStatsResponse,
    VolunteerResponse,
    PublicVolunteerRegistration,
    RegistrationSuccessResponse
)
from core.security import get_password_hash

router = APIRouter()


@router.post("/register", response_model=RegistrationSuccessResponse, status_code=status.HTTP_201_CREATED)
def public_volunteer_registration(
    registration_data: PublicVolunteerRegistration,
    db: Session = Depends(get_db)
):
    """
    PUBLIC endpoint for volunteer self-registration.
    No authentication required - this is the entry point for new volunteers.
    
    Creates a volunteer account with 'pending' status that requires coordinator approval.
    """
    # Check if email already exists
    existing = db.query(Volunteer).filter(Volunteer.email == registration_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A volunteer with this email already exists"
        )
    
    # Create username from email
    username = registration_data.email.lower().strip()
    
    # Check if username exists
    existing_username = db.query(Volunteer).filter(Volunteer.username == username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken"
        )
    
    # Hash password
    hashed_password = get_password_hash(registration_data.password)
    
    # Create volunteer with PENDING status
    volunteer_data = registration_data.dict(exclude={'password'})
    volunteer = Volunteer(
        **volunteer_data,
        username=username,
        hashed_password=hashed_password,
        application_status='pending',  # Requires coordinator approval
        account_status='active',
        application_date=datetime.utcnow()
    )
    
    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    
    # TODO: Send welcome email to volunteer
    # TODO: Send notification to unit coordinator
    
    return RegistrationSuccessResponse(
        message="Registration successful! Your application is pending coordinator approval.",
        volunteer_id=volunteer.id,
        email=volunteer.email,
        status=volunteer.application_status
    )


@router.get("/", response_model=VolunteerListResponse)
def list_volunteers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List volunteers in current tenant."""
    volunteers = db.query(Volunteer).filter(
        Volunteer.tenant_id == current_user.tenant_id
    ).offset(skip).limit(limit).all()
    total = db.query(Volunteer).filter(Volunteer.tenant_id == current_user.tenant_id).count()
    return VolunteerListResponse(total=total, items=volunteers)


@router.get("/stats", response_model=VolunteerStatsResponse)
def get_volunteer_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get volunteer statistics for dashboard."""
    base_query = db.query(Volunteer).filter(Volunteer.tenant_id == current_user.tenant_id)
    
    total = base_query.count()
    approved = base_query.filter(Volunteer.application_status == VolunteerStatus.APPROVED).count()
    pending = base_query.filter(Volunteer.application_status == VolunteerStatus.PENDING).count()
    incomplete = base_query.filter(Volunteer.application_status == VolunteerStatus.INCOMPLETE).count()
    working = base_query.filter(Volunteer.application_status == VolunteerStatus.WORKING).count()
    
    return VolunteerStatsResponse(
        total_volunteers=total,
        approved_volunteers=approved,
        pending_applications=pending,
        incomplete_applications=incomplete,
        working_volunteers=working
    )


@router.get("/{volunteer_id}", response_model=VolunteerResponse)
def get_volunteer(
    volunteer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single volunteer by ID."""
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    return volunteer


@router.patch("/{volunteer_id}/approve", response_model=VolunteerResponse)
def approve_volunteer(
    volunteer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a pending volunteer application."""
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    volunteer.application_status = 'approved'
    volunteer.approval_date = datetime.utcnow()
    volunteer.approved_by = current_user.id
    
    db.commit()
    db.refresh(volunteer)
    
    # TODO: Send approval email to volunteer
    
    return volunteer


@router.delete("/{volunteer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_volunteer(
    volunteer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a volunteer."""
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    db.delete(volunteer)
    db.commit()
    
    return None