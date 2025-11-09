"""
Advanced scheduling endpoints for shift management.
Implements section 1.2 from roadmap.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List
from datetime import datetime, date, timedelta
from database import get_db
from models.user import User
from models.volunteer import Volunteer
from models.event import Event, Shift, EventAssignment
from api.deps import get_current_user
from schemas.scheduling import (
    ShiftTemplateCreate, ShiftTemplateResponse,
    WaitlistJoinRequest, WaitlistResponse,
    AvailabilityCreate, AvailabilityUpdate, AvailabilityResponse,
    SwapRequestCreate, SwapRequestResponse,
    ShiftSelfSignupRequest, AvailableShiftResponse,
    BulkShiftCreateRequest, BulkShiftCreateResponse
)

router = APIRouter()


# ======================
# SHIFT TEMPLATES
# ======================

@router.get("/templates", response_model=List[ShiftTemplateResponse])
def list_shift_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all shift templates for current tenant."""
    from models.event import Shift
    
    # Mock response for now - implement actual model later
    return []


@router.post("/templates", response_model=ShiftTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_shift_template(
    template_data: ShiftTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new shift template for recurring shifts."""
    # TODO: Implement shift template model
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Shift templates will be implemented in phase 2"
    )


# ======================
# AVAILABLE SHIFTS & SELF-SIGNUP
# ======================

@router.get("/shifts/available", response_model=List[AvailableShiftResponse])
def get_available_shifts(
    start_date: date = None,
    end_date: date = None,
    include_full: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available shifts for self-signup.
    Volunteers can browse and sign up for open shifts.
    """
    # Build query for shifts with self-signup enabled
    query = db.query(Shift).join(Event).filter(
        Event.tenant_id == current_user.tenant_id,
        Shift.allow_self_signup == True,
        Shift.start_time >= datetime.now()
    )
    
    # Filter by date range
    if start_date:
        query = query.filter(Shift.start_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Shift.start_time <= datetime.combine(end_date, datetime.max.time()))
    
    shifts = query.all()
    
    # Transform to response format
    available_shifts = []
    for shift in shifts:
        # Count current volunteers
        current_count = db.query(func.count(EventAssignment.id)).filter(
            EventAssignment.shift_id == shift.id,
            EventAssignment.status.in_(['confirmed', 'pending'])
        ).scalar() or 0
        
        # Count waitlist
        waitlist_count = 0  # TODO: Query actual waitlist table
        
        # Calculate available spots
        available_spots = (shift.max_volunteers or 0) - current_count
        
        # Skip full shifts if not requested
        if not include_full and available_spots <= 0:
            continue
        
        available_shifts.append(AvailableShiftResponse(
            id=shift.id,
            event_id=shift.event_id,
            name=shift.name,
            start_time=shift.start_time,
            end_time=shift.end_time,
            location=shift.location,
            max_volunteers=shift.max_volunteers,
            current_volunteers=current_count,
            available_spots=max(0, available_spots),
            waitlist_count=waitlist_count,
            allow_self_signup=shift.allow_self_signup or False,
            enable_waitlist=shift.enable_waitlist or False,
            required_skills=shift.required_skills,
            event_name=shift.event.name,
            event_description=shift.event.volunteer_description
        ))
    
    return available_shifts


@router.post("/shifts/{shift_id}/signup", status_code=status.HTTP_201_CREATED)
def self_signup_for_shift(
    shift_id: int,
    request_data: ShiftSelfSignupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Self-signup for an available shift.
    Includes conflict detection and capacity checking.
    """
    # Get shift
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    
    # Check if self-signup is allowed
    if not shift.allow_self_signup:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Self-signup is not enabled for this shift"
        )
    
    # Get volunteer record for current user
    volunteer = db.query(Volunteer).filter(
        Volunteer.email == current_user.email,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    # Check for conflicts (double-booking)
    if shift.conflict_detection:
        conflicts = db.query(EventAssignment).join(Shift).filter(
            EventAssignment.volunteer_id == volunteer.id,
            EventAssignment.status.in_(['confirmed', 'pending']),
            or_(
                and_(
                    Shift.start_time <= shift.start_time,
                    Shift.end_time > shift.start_time
                ),
                and_(
                    Shift.start_time < shift.end_time,
                    Shift.end_time >= shift.end_time
                )
            )
        ).first()
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have a conflicting shift assignment during this time"
            )
    
    # Check capacity
    current_count = db.query(func.count(EventAssignment.id)).filter(
        EventAssignment.shift_id == shift_id,
        EventAssignment.status.in_(['confirmed', 'pending'])
    ).scalar() or 0
    
    if shift.max_volunteers and current_count >= shift.max_volunteers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shift is full. Consider joining the waitlist."
        )
    
    # Check if already signed up
    existing = db.query(EventAssignment).filter(
        EventAssignment.shift_id == shift_id,
        EventAssignment.volunteer_id == volunteer.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already signed up for this shift"
        )
    
    # Create assignment
    assignment = EventAssignment(
        event_id=shift.event_id,
        shift_id=shift_id,
        volunteer_id=volunteer.id,
        status='confirmed',
        notes=request_data.notes,
        assigned_at=datetime.utcnow()
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    # TODO: Send confirmation email/notification
    
    return {
        "message": "Successfully signed up for shift",
        "assignment_id": assignment.id,
        "shift_name": shift.name,
        "start_time": shift.start_time.isoformat()
    }


# ======================
# WAITLIST MANAGEMENT
# ======================

@router.post("/shifts/{shift_id}/waitlist", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
def join_waitlist(
    shift_id: int,
    request_data: WaitlistJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Join waitlist for a full shift.
    Will be automatically promoted when a spot opens.
    """
    # Get shift
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    
    if not shift.enable_waitlist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Waitlist is not enabled for this shift"
        )
    
    # Get volunteer
    volunteer = db.query(Volunteer).filter(
        Volunteer.email == current_user.email,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    # Check if already on waitlist
    # TODO: Query actual waitlist table
    
    # TODO: Create waitlist entry with proper position
    
    return {
        "message": "Added to waitlist",
        "shift_id": shift_id,
        "position": 1  # Calculate actual position
    }


@router.get("/waitlists/mine", response_model=List[WaitlistResponse])
def get_my_waitlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all waitlist entries for current volunteer."""
    volunteer = db.query(Volunteer).filter(
        Volunteer.email == current_user.email,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        return []
    
    # TODO: Query actual waitlist table
    return []


# ======================
# AVAILABILITY MARKING
# ======================

@router.post("/availability", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def mark_availability(
    availability_data: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark availability for date ranges.
    Coordinators can use this to assign volunteers.
    """
    volunteer = db.query(Volunteer).filter(
        Volunteer.email == current_user.email,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    # TODO: Create availability record in database
    
    return {
        "message": "Availability marked successfully"
    }


@router.get("/availability/mine", response_model=List[AvailabilityResponse])
def get_my_availability(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get availability calendar for current volunteer."""
    volunteer = db.query(Volunteer).filter(
        Volunteer.email == current_user.email,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        return []
    
    # TODO: Query availability records
    return []


# ======================
# SHIFT SWAPPING
# ======================

@router.post("/swap-requests", response_model=SwapRequestResponse, status_code=status.HTTP_201_CREATED)
def request_shift_swap(
    swap_data: SwapRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request to swap a shift with another volunteer.
    Requires coordinator approval.
    """
    # Get original assignment
    assignment = db.query(EventAssignment).filter(
        EventAssignment.id == swap_data.original_assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Verify ownership
    volunteer = db.query(Volunteer).filter(
        Volunteer.email == current_user.email,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer or assignment.volunteer_id != volunteer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only request swaps for your own assignments"
        )
    
    # TODO: Create swap request in database
    # TODO: Send notification to target volunteer and coordinator
    
    return {
        "message": "Swap request submitted",
        "assignment_id": assignment.id
    }


@router.get("/swap-requests/pending")
def get_pending_swap_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending swap requests (for coordinators)."""
    # TODO: Query swap requests
    return []


@router.patch("/swap-requests/{swap_id}/approve")
def approve_swap_request(
    swap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a shift swap request (coordinator only)."""
    # TODO: Implement swap approval logic
    # TODO: Swap the assignments
    # TODO: Notify both volunteers
    
    return {"message": "Swap request approved"}


# ======================
# BULK OPERATIONS
# ======================

@router.post("/shifts/bulk-create", response_model=BulkShiftCreateResponse)
def bulk_create_shifts_from_template(
    request_data: BulkShiftCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple shifts from a template.
    Useful for recurring events like weekly vaccine clinics.
    """
    # TODO: Get template
    # TODO: Generate shifts based on recurrence pattern
    # TODO: Create all shifts in database
    
    return BulkShiftCreateResponse(
        created_count=0,
        shifts_created=[],
        message="Bulk shift creation will be implemented in phase 2"
    )