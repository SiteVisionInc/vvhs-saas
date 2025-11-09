"""
Behavioral Health API endpoints - Facility & Bed Management.
Handles facility management, bed availability tracking, and bed search.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.behavioral_health import (
    BHFacility, BHBedSnapshot
)
from schemas.behavioral_health import (
    BHFacilityCreate, BHFacilityUpdate, BHFacilityResponse,
    BHBedSnapshotCreate, BHBedSnapshotResponse,
    BedSearchRequest, BedSearchResult,
    StaleBedsAlert
)
from api.deps import get_current_user
from services.audit import log_action

router = APIRouter()


# ==================== FACILITY CRUD ====================

@router.post("/", response_model=BHFacilityResponse, status_code=status.HTTP_201_CREATED)
def create_facility(
    facility_data: BHFacilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new behavioral health facility."""
    facility = BHFacility(**facility_data.dict())
    
    db.add(facility)
    db.commit()
    db.refresh(facility)
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_facility.created",
        resource_type="bh_facility",
        resource_id=facility.id,
        description=f"Created facility: {facility.name}",
        new_values=facility_data.dict()
    )
    
    return facility


@router.get("/{facility_id}", response_model=BHFacilityResponse)
def get_facility(
    facility_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get facility by ID."""
    facility = db.query(BHFacility).filter(
        BHFacility.id == facility_id,
        BHFacility.tenant_id == current_user.tenant_id
    ).first()
    
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    return facility


@router.put("/{facility_id}", response_model=BHFacilityResponse)
def update_facility(
    facility_id: int,
    facility_data: BHFacilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update facility information."""
    facility = db.query(BHFacility).filter(
        BHFacility.id == facility_id,
        BHFacility.tenant_id == current_user.tenant_id
    ).first()
    
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    # Update fields
    for field, value in facility_data.dict(exclude_unset=True).items():
        setattr(facility, field, value)
    
    facility.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(facility)
    
    return facility


@router.get("/", response_model=List[BHFacilityResponse])
def list_facilities(
    skip: int = 0,
    limit: int = 100,
    facility_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all facilities with optional filtering."""
    query = db.query(BHFacility).filter(
        BHFacility.tenant_id == current_user.tenant_id
    )
    
    if facility_type:
        query = query.filter(BHFacility.facility_type == facility_type)
    
    if is_active is not None:
        query = query.filter(BHFacility.is_active == is_active)
    
    facilities = query.offset(skip).limit(limit).all()
    return facilities


# ==================== BED AVAILABILITY ====================

@router.post("/beds/update", response_model=BHBedSnapshotResponse)
def update_bed_availability(
    bed_data: BHBedSnapshotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update bed availability (manual entry by facility coordinator).
    Creates a new snapshot or updates existing one.
    """
    # Verify facility exists
    facility = db.query(BHFacility).filter(
        BHFacility.id == bed_data.facility_id,
        BHFacility.tenant_id == current_user.tenant_id
    ).first()
    
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    # Find existing snapshot for this facility/bed type
    existing = db.query(BHBedSnapshot).filter(
        and_(
            BHBedSnapshot.facility_id == bed_data.facility_id,
            BHBedSnapshot.bed_type == bed_data.bed_type,
            BHBedSnapshot.unit_name == bed_data.unit_name
        )
    ).first()
    
    if existing:
        # Update existing snapshot
        existing.capacity_total = bed_data.capacity_total
        existing.capacity_available = bed_data.capacity_available
        existing.constraints = bed_data.constraints
        existing.last_reported_at = datetime.utcnow()
        existing.reported_by = current_user.id
        
        db.commit()
        db.refresh(existing)
        
        snapshot = existing
    else:
        # Create new snapshot
        snapshot = BHBedSnapshot(
            **bed_data.dict(exclude={'reported_by'}),
            last_reported_at=datetime.utcnow(),
            reported_by=current_user.id
        )
        
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
    
    log_action(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="bh_beds.updated",
        resource_type="bh_bed_snapshot",
        resource_id=snapshot.id,
        description=f"Updated beds for {facility.name}: {snapshot.capacity_available}/{snapshot.capacity_total}",
        new_values=bed_data.dict()
    )
    
    return snapshot


@router.get("/{facility_id}/beds", response_model=List[BHBedSnapshotResponse])
def get_facility_beds(
    facility_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bed snapshots for a facility."""
    facility = db.query(BHFacility).filter(
        BHFacility.id == facility_id,
        BHFacility.tenant_id == current_user.tenant_id
    ).first()
    
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    snapshots = db.query(BHBedSnapshot).filter(
        BHBedSnapshot.facility_id == facility_id
    ).all()
    
    return snapshots


# ==================== BED SEARCH ====================

@router.post("/search", response_model=List[BedSearchResult])
def search_beds(
    search_params: BedSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for available beds based on criteria.
    Core workflow for clinicians finding placement.
    """
    # Base query
    query = db.query(
        BHBedSnapshot,
        BHFacility
    ).join(
        BHFacility,
        BHBedSnapshot.facility_id == BHFacility.id
    ).filter(
        and_(
            BHFacility.tenant_id == current_user.tenant_id,
            BHFacility.is_active == True,
            BHBedSnapshot.capacity_available >= search_params.min_available
        )
    )
    
    # Filter by facility type
    if search_params.facility_type:
        query = query.filter(BHFacility.facility_type == search_params.facility_type)
    
    # Filter by bed type
    if search_params.bed_type:
        query = query.filter(BHBedSnapshot.bed_type == search_params.bed_type)
    
    # Filter by region
    if search_params.region_id:
        query = query.filter(BHFacility.region_id == search_params.region_id)
    
    # Filter by capabilities
    if search_params.capabilities:
        for capability in search_params.capabilities:
            query = query.filter(
                BHFacility.capabilities.contains([capability])
            )
    
    # Execute query
    results = query.all()
    
    # Build response
    search_results = []
    for snapshot, facility in results:
        # Check age constraints
        if search_params.patient_age and snapshot.constraints:
            age_min = snapshot.constraints.get('age_min')
            age_max = snapshot.constraints.get('age_max')
            
            if age_min and search_params.patient_age < age_min:
                continue
            if age_max and search_params.patient_age > age_max:
                continue
        
        # Check gender constraints
        if search_params.patient_gender and snapshot.constraints:
            required_gender = snapshot.constraints.get('gender')
            if required_gender and required_gender != search_params.patient_gender:
                continue
        
        # TODO: Calculate distance if lat/lng provided
        distance_miles = None
        if search_params.latitude and search_params.longitude and facility.address:
            # Implement haversine distance calculation
            pass
        
        search_results.append(BedSearchResult(
            facility_id=facility.id,
            facility_name=facility.name,
            facility_type=facility.facility_type,
            bed_type=snapshot.bed_type,
            available_beds=snapshot.capacity_available,
            total_beds=snapshot.capacity_total,
            distance_miles=distance_miles,
            contact_phone=facility.contact_phone,
            last_updated=snapshot.last_reported_at,
            is_stale=snapshot.is_stale
        ))
    
    # Sort by available beds (descending) and distance
    search_results.sort(
        key=lambda x: (-x.available_beds, x.distance_miles or 999999)
    )
    
    return search_results


# ==================== STALE DATA ALERTS ====================

@router.get("/beds/stale-alerts", response_model=List[StaleBedsAlert])
def get_stale_bed_alerts(
    hours_threshold: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get facilities with stale bed data (>24 hours old).
    Used by state admins to ensure data quality.
    """
    threshold_time = datetime.utcnow() - timedelta(hours=hours_threshold)
    
    # Find latest snapshot per facility
    latest_snapshots = db.query(
        BHBedSnapshot.facility_id,
        func.max(BHBedSnapshot.last_reported_at).label('latest_update')
    ).group_by(
        BHBedSnapshot.facility_id
    ).subquery()
    
    # Get facilities with stale data
    stale_facilities = db.query(
        BHFacility,
        latest_snapshots.c.latest_update
    ).join(
        latest_snapshots,
        BHFacility.id == latest_snapshots.c.facility_id
    ).filter(
        and_(
            BHFacility.tenant_id == current_user.tenant_id,
            BHFacility.is_active == True,
            latest_snapshots.c.latest_update < threshold_time
        )
    ).all()
    
    # Build response
    alerts = []
    for facility, latest_update in stale_facilities:
        hours_stale = (datetime.utcnow() - latest_update).total_seconds() / 3600
        
        alerts.append(StaleBedsAlert(
            facility_id=facility.id,
            facility_name=facility.name,
            last_updated=latest_update,
            hours_stale=hours_stale,
            contact_phone=facility.contact_phone
        ))
    
    # Sort by staleness (most stale first)
    alerts.sort(key=lambda x: -x.hours_stale)
    
    return alerts


# ==================== HL7/FHIR FEED ====================

@router.post("/beds/hl7-feed")
async def process_hl7_feed(
    hl7_message: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process automated HL7/FHIR feed from facility EHR.
    Updates bed availability automatically.
    """
    # TODO: Implement HL7 message parsing
    # This would parse ADT messages for bed census
    
    return {
        "status": "not_implemented",
        "message": "HL7 feed processing will be implemented in Phase 2"
    }
