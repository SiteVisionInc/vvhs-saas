# api/app/api/v1/time_tracking.py
"""
Time tracking endpoints for volunteer hours.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets

from database import get_db
from models.user import User
from models.volunteer import Volunteer
from models.event import Event
from models.time_tracking import TimeEntry, EventQRCode, CheckinSession
from api.deps import get_current_user
from schemas.time_tracking import (
    TimeEntryCreate,
    TimeEntryBulkCreate,
    TimeEntryUpdate,
    TimeEntryResponse,
    TimeEntryApproval,
    BulkTimeEntryApproval,
    QRCodeCreate,
    QRCodeResponse,
    CheckinRequest,
    CheckoutRequest,
    CheckinResponse,
    VolunteerHoursReport,
    PendingApprovalsReport
)

router = APIRouter()


# =============== Time Entries ===============

@router.get("/entries", response_model=List[TimeEntryResponse])
def list_time_entries(
    volunteer_id: Optional[int] = None,
    event_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List time entries with filters."""
    print(f"\n=== TIME ENTRIES API CALLED ===")
    print(f"User: {current_user.username} (tenant {current_user.tenant_id})")
    print(f"Filters: volunteer_id={volunteer_id}, event_id={event_id}, status={status}")
    
    query = db.query(TimeEntry).filter(
        TimeEntry.tenant_id == current_user.tenant_id
    )
    
    if volunteer_id:
        query = query.filter(TimeEntry.volunteer_id == volunteer_id)
    if event_id:
        query = query.filter(TimeEntry.event_id == event_id)
    if status:
        query = query.filter(TimeEntry.status == status)
    if start_date:
        query = query.filter(TimeEntry.check_in_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.check_in_time <= end_date)
    
    entries = query.order_by(TimeEntry.check_in_time.desc()).offset(skip).limit(limit).all()
    
    print(f"Found {len(entries)} entries")
    
    # Enhance with volunteer/event names
    result = []
    for entry in entries:
        volunteer_name = "Unknown Volunteer"
        event_name = None
        
        # Get volunteer info - don't fail if volunteer not found
        try:
            volunteer = db.query(Volunteer).filter(Volunteer.id == entry.volunteer_id).first()
            if volunteer:
                volunteer_name = f"{volunteer.first_name} {volunteer.last_name}"
            else:
                print(f"⚠️ Warning: Volunteer {entry.volunteer_id} not found for entry {entry.id}")
        except Exception as e:
            print(f"⚠️ Error fetching volunteer {entry.volunteer_id}: {e}")
        
        # Get event info - don't fail if event not found
        try:
            if entry.event_id:
                event = db.query(Event).filter(Event.id == entry.event_id).first()
                if event:
                    event_name = event.name
        except Exception as e:
            print(f"⚠️ Error fetching event {entry.event_id}: {e}")
        
        # Build response object
        entry_dict = {
            'id': entry.id,
            'tenant_id': entry.tenant_id,
            'volunteer_id': entry.volunteer_id,
            'event_id': entry.event_id,
            'shift_id': entry.shift_id,
            'check_in_time': entry.check_in_time,
            'check_out_time': entry.check_out_time,
            'duration_minutes': entry.duration_minutes,
            'hours_decimal': float(entry.hours_decimal) if entry.hours_decimal else None,
            'entry_method': entry.entry_method,
            'status': entry.status,
            'approved_by': entry.approved_by,
            'approved_at': entry.approved_at,
            'volunteer_notes': entry.volunteer_notes,
            'coordinator_notes': entry.coordinator_notes,
            'created_at': entry.created_at,
            'volunteer_name': volunteer_name,
            'event_name': event_name
        }
        
        print(f"  ✓ Entry {entry.id}: {volunteer_name} - {entry.hours_decimal} hrs - {entry.status}")
        result.append(TimeEntryResponse(**entry_dict))
    
    print(f"Returning {len(result)} entries")
    print("=== END TIME ENTRIES API ===\n")
    
    return result


@router.post("/entries", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    entry_data: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a single time entry (manual or coordinator entry)."""
    # Verify volunteer exists
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == entry_data.volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Create time entry
    entry = TimeEntry(
        tenant_id=current_user.tenant_id,
        **entry_data.dict(),
        submitted_by=current_user.id,
        status='pending'  # Requires approval
    )
    
    # Calculate duration if check-out provided
    if entry.check_out_time:
        entry.calculate_duration()
    
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return TimeEntryResponse(
        **entry.__dict__,
        volunteer_name=volunteer.full_name,
        event_name=entry.event.name if entry.event else None
    )


@router.post("/entries/bulk", status_code=status.HTTP_201_CREATED)
def create_bulk_time_entries(
    bulk_data: TimeEntryBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk create time entries (coordinator convenience feature)."""
    created_entries = []
    errors = []
    
    for entry_data in bulk_data.entries:
        try:
            volunteer = db.query(Volunteer).filter(
                Volunteer.id == entry_data['volunteer_id'],
                Volunteer.tenant_id == current_user.tenant_id
            ).first()
            
            if not volunteer:
                errors.append(f"Volunteer {entry_data['volunteer_id']} not found")
                continue
            
            entry = TimeEntry(
                tenant_id=current_user.tenant_id,
                volunteer_id=entry_data['volunteer_id'],
                event_id=bulk_data.event_id,
                check_in_time=entry_data['check_in_time'],
                check_out_time=entry_data.get('check_out_time'),
                volunteer_notes=entry_data.get('notes'),
                entry_method='manual',
                submitted_by=current_user.id,
                status='pending'
            )
            
            if entry.check_out_time:
                entry.calculate_duration()
            
            db.add(entry)
            created_entries.append(entry.id)
            
        except Exception as e:
            errors.append(f"Error for volunteer {entry_data.get('volunteer_id')}: {str(e)}")
    
    db.commit()
    
    return {
        "message": f"Created {len(created_entries)} time entries",
        "created_count": len(created_entries),
        "created_ids": created_entries,
        "errors": errors
    }


@router.patch("/entries/{entry_id}/approve", response_model=TimeEntryResponse)
def approve_time_entry(
    entry_id: int,
    approval: TimeEntryApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a time entry."""
    entry = db.query(TimeEntry).filter(
        TimeEntry.id == entry_id,
        TimeEntry.tenant_id == current_user.tenant_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    if entry.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entry has already been processed"
        )
    
    # Update status
    entry.status = approval.status
    entry.approved_by = current_user.id
    entry.approved_at = datetime.utcnow()
    entry.coordinator_notes = approval.coordinator_notes
    
    if approval.status == 'rejected':
        entry.rejection_reason = approval.rejection_reason
    
    # Allow coordinator to override hours
    if approval.hours_override and approval.status == 'approved':
        entry.hours_decimal = approval.hours_override
        entry.duration_minutes = int(float(approval.hours_override) * 60)
    
    db.commit()
    db.refresh(entry)
    
    return TimeEntryResponse(
        **entry.__dict__,
        volunteer_name=entry.volunteer.full_name,
        event_name=entry.event.name if entry.event else None
    )


@router.post("/entries/bulk-approve")
def bulk_approve_entries(
    approval: BulkTimeEntryApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk approve or reject multiple time entries."""
    entries = db.query(TimeEntry).filter(
        TimeEntry.id.in_(approval.entry_ids),
        TimeEntry.tenant_id == current_user.tenant_id,
        TimeEntry.status == 'pending'
    ).all()
    
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending entries found"
        )
    
    updated_count = 0
    for entry in entries:
        entry.status = 'approved' if approval.action == 'approve' else 'rejected'
        entry.approved_by = current_user.id
        entry.approved_at = datetime.utcnow()
        if approval.notes:
            entry.coordinator_notes = approval.notes
        updated_count += 1
    
    db.commit()
    
    return {
        "message": f"{approval.action.capitalize()}d {updated_count} time entries",
        "updated_count": updated_count
    }


@router.get("/entries/pending", response_model=PendingApprovalsReport)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending time entries requiring approval."""
    entries = db.query(TimeEntry).filter(
        TimeEntry.tenant_id == current_user.tenant_id,
        TimeEntry.status == 'pending'
    ).order_by(TimeEntry.check_in_time.desc()).all()
    
    total_hours = sum(float(e.hours_decimal or 0) for e in entries)
    oldest_date = min((e.check_in_time for e in entries), default=None)
    
    entry_responses = [
        TimeEntryResponse(
            **e.__dict__,
            volunteer_name=e.volunteer.full_name,
            event_name=e.event.name if e.event else None
        )
        for e in entries
    ]
    
    return PendingApprovalsReport(
        total_pending=len(entries),
        total_hours_pending=total_hours,
        oldest_entry_date=oldest_date,
        entries=entry_responses
    )


# =============== QR Codes ===============

@router.post("/qr-codes", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED)
def create_qr_code(
    qr_data: QRCodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a QR code for an event or shift."""
    if not qr_data.event_id and not qr_data.shift_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify either event_id or shift_id"
        )
    
    # Generate unique hash
    random_data = f"{qr_data.event_id}{qr_data.shift_id}{datetime.utcnow().isoformat()}{secrets.token_hex(16)}"
    qr_hash = hashlib.sha256(random_data.encode()).hexdigest()[:32]
    
    qr_code = EventQRCode(
        **qr_data.dict(),
        qr_code_hash=qr_hash,
        qr_code_url=f"https://vvhs.org/checkin/{qr_hash}",
        created_by=current_user.id
    )
    
    db.add(qr_code)
    db.commit()
    db.refresh(qr_code)
    
    return QRCodeResponse(
        **qr_code.__dict__,
        event_name=qr_code.event.name if qr_code.event else None
    )


@router.get("/events/{event_id}/qr-code", response_model=QRCodeResponse)
def get_event_qr_code(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get QR code for an event."""
    qr_code = db.query(EventQRCode).filter(
        EventQRCode.event_id == event_id,
        EventQRCode.is_active == True
    ).order_by(EventQRCode.created_at.desc()).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active QR code found for this event"
        )
    
    return QRCodeResponse(
        **qr_code.__dict__,
        event_name=qr_code.event.name if qr_code.event else None
    )


# =============== Check-in/Check-out ===============

@router.post("/checkin", response_model=CheckinResponse)
def volunteer_checkin(
    checkin: CheckinRequest,
    db: Session = Depends(get_db)
):
    """Volunteer check-in via QR code or direct entry."""
    # Verify QR code if provided
    qr_code = None
    if checkin.qr_code_hash:
        qr_code = db.query(EventQRCode).filter(
            EventQRCode.qr_code_hash == checkin.qr_code_hash
        ).first()
        
        if not qr_code or not qr_code.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired QR code"
            )
    
    # Get volunteer
    if not checkin.volunteer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Volunteer ID is required"
        )
    
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == checkin.volunteer_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Create check-in session
    session = CheckinSession(
        volunteer_id=checkin.volunteer_id,
        event_id=checkin.event_id or (qr_code.event_id if qr_code else None),
        qr_code_id=qr_code.id if qr_code else None,
        check_in_time=datetime.utcnow(),
        device_info=str(checkin.device_info) if checkin.device_info else None,
        status='active'
    )
    
    db.add(session)
    
    # Create time entry
    time_entry = TimeEntry(
        tenant_id=volunteer.tenant_id,
        volunteer_id=volunteer.id,
        event_id=checkin.event_id or (qr_code.event_id if qr_code else None),
        check_in_time=datetime.utcnow(),
        entry_method='qr_code' if qr_code else 'kiosk',
        check_in_lat=checkin.latitude,
        check_in_lng=checkin.longitude,
        status='pending'
    )
    
    db.add(time_entry)
    
    # Update QR code use count
    if qr_code:
        qr_code.use_count += 1
    
    db.commit()
    db.refresh(session)
    db.refresh(time_entry)
    
    return CheckinResponse(
        success=True,
        message="Successfully checked in",
        session_id=session.id,
        time_entry_id=time_entry.id,
        volunteer_name=volunteer.full_name,
        event_name=time_entry.event.name if time_entry.event else None,
        check_in_time=time_entry.check_in_time
    )


@router.post("/checkout")
def volunteer_checkout(
    checkout: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Volunteer check-out."""
    time_entry = None
    
    if checkout.time_entry_id:
        time_entry = db.query(TimeEntry).filter(
            TimeEntry.id == checkout.time_entry_id
        ).first()
    elif checkout.session_id:
        session = db.query(CheckinSession).filter(
            CheckinSession.id == checkout.session_id,
            CheckinSession.status == 'active'
        ).first()
        
        if session:
            time_entry = db.query(TimeEntry).filter(
                TimeEntry.volunteer_id == session.volunteer_id,
                TimeEntry.event_id == session.event_id,
                TimeEntry.check_out_time.is_(None)
            ).order_by(TimeEntry.check_in_time.desc()).first()
            
            if session:
                session.check_out_time = datetime.utcnow()
                session.status = 'completed'
    
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active check-in found"
        )
    
    # Update time entry
    time_entry.check_out_time = datetime.utcnow()
    time_entry.check_out_lat = checkout.latitude
    time_entry.check_out_lng = checkout.longitude
    if checkout.notes:
        time_entry.volunteer_notes = checkout.notes
    
    time_entry.calculate_duration()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Successfully checked out",
        "hours": float(time_entry.hours_decimal or 0)
    }


# =============== Reports ===============

@router.get("/reports/volunteer-hours/{volunteer_id}", response_model=VolunteerHoursReport)
def get_volunteer_hours_report(
    volunteer_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hours report for a specific volunteer."""
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    query = db.query(TimeEntry).filter(TimeEntry.volunteer_id == volunteer_id)
    
    if start_date:
        query = query.filter(TimeEntry.check_in_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.check_in_time <= end_date)
    
    entries = query.all()
    
    total_hours = sum(float(e.hours_decimal or 0) for e in entries if e.hours_decimal)
    approved_hours = sum(float(e.hours_decimal or 0) for e in entries if e.status == 'approved' and e.hours_decimal)
    pending_hours = sum(float(e.hours_decimal or 0) for e in entries if e.status == 'pending' and e.hours_decimal)
    
    return VolunteerHoursReport(
        volunteer_id=volunteer.id,
        volunteer_name=volunteer.full_name,
        total_hours=total_hours,
        approved_hours=approved_hours,
        pending_hours=pending_hours,
        entry_count=len(entries),
        date_range_start=start_date,
        date_range_end=end_date
    )