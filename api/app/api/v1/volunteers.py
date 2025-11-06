"""Volunteer management endpoints (stub for Phase 1)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.volunteer import Volunteer, VolunteerStatus
from api.deps import get_current_user
from schemas.volunteer import VolunteerListResponse, VolunteerStatsResponse

router = APIRouter()

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

# TODO: Add full CRUD endpoints for volunteers
