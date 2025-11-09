# api/app/api/v1/training.py
"""
Training management endpoints.
Handles training records, certifications, and TRAIN integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List
from datetime import date, timedelta

from database import get_db
from models.user import User
from models.volunteer import Volunteer
from models.training import TrainingCourse, VolunteerTraining, Certification
from api.deps import get_current_user
from schemas.training import (
    TrainingCourseResponse,
    VolunteerTrainingCreate,
    VolunteerTrainingResponse,
    CertificationCreate,
    CertificationUpdate,
    CertificationResponse,
    TrainingStatusSummary,
    ExpiringTrainingReport,
    TRAINSyncRequest,
    TRAINSyncResponse
)
from services.train import train_service

router = APIRouter()


# =============== Training Courses ===============

@router.get("/courses", response_model=List[TrainingCourseResponse])
def list_training_courses(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    required_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all training courses for current tenant."""
    query = db.query(TrainingCourse).filter(
        TrainingCourse.tenant_id == current_user.tenant_id
    )
    
    if category:
        query = query.filter(TrainingCourse.category == category)
    if required_only:
        query = query.filter(TrainingCourse.is_required == True)
    
    courses = query.offset(skip).limit(limit).all()
    return courses


@router.get("/courses/{course_id}", response_model=TrainingCourseResponse)
def get_training_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get training course by ID."""
    course = db.query(TrainingCourse).filter(
        TrainingCourse.id == course_id,
        TrainingCourse.tenant_id == current_user.tenant_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training course not found"
        )
    
    return course


# =============== Volunteer Training Records ===============

@router.get("/volunteers/{volunteer_id}/training", response_model=List[VolunteerTrainingResponse])
def get_volunteer_training(
    volunteer_id: int,
    include_expired: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all training records for a volunteer."""
    # Verify volunteer exists and belongs to tenant
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    query = db.query(VolunteerTraining).filter(
        VolunteerTraining.volunteer_id == volunteer_id
    )
    
    if not include_expired:
        query = query.filter(
            or_(
                VolunteerTraining.expiration_date.is_(None),
                VolunteerTraining.expiration_date >= date.today()
            )
        )
    
    trainings = query.all()
    
    # Enhance with course details
    result = []
    for training in trainings:
        training_dict = {
            **training.__dict__,
            'course_name': training.course.name,
            'course_provider': training.course.provider,
            'course_category': training.course.category,
            'is_expired': training.is_expired
        }
        result.append(VolunteerTrainingResponse(**training_dict))
    
    return result


@router.post("/volunteers/{volunteer_id}/training", response_model=VolunteerTrainingResponse, status_code=status.HTTP_201_CREATED)
def add_training_record(
    volunteer_id: int,
    training_data: VolunteerTrainingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a training record for a volunteer (manual entry)."""
    # Verify volunteer
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Verify course exists
    course = db.query(TrainingCourse).filter(
        TrainingCourse.id == training_data.course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training course not found"
        )
    
    # Create training record
    training = VolunteerTraining(**training_data.dict())
    training.synced_from_train = False
    training.status = 'active'
    
    db.add(training)
    db.commit()
    db.refresh(training)
    
    return VolunteerTrainingResponse(
        **training.__dict__,
        course_name=course.name,
        course_provider=course.provider,
        course_category=course.category,
        is_expired=training.is_expired
    )


@router.get("/volunteers/{volunteer_id}/training-status", response_model=TrainingStatusSummary)
def get_training_status(
    volunteer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get training compliance status for a volunteer."""
    # Verify volunteer
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Get all required courses
    required_courses = db.query(TrainingCourse).filter(
        TrainingCourse.tenant_id == current_user.tenant_id,
        TrainingCourse.is_required == True
    ).all()
    
    # Get volunteer's training records
    trainings = db.query(VolunteerTraining).filter(
        VolunteerTraining.volunteer_id == volunteer_id
    ).all()
    
    # Calculate statistics
    completed_course_ids = {t.course_id for t in trainings if not t.is_expired}
    expired_count = sum(1 for t in trainings if t.is_expired)
    
    # Expiring soon (within 90 days)
    expiring_soon = sum(
        1 for t in trainings
        if t.expiration_date and 
        not t.is_expired and
        t.expiration_date <= date.today() + timedelta(days=90)
    )
    
    # Missing required courses
    missing_required = [
        course.name 
        for course in required_courses 
        if course.id not in completed_course_ids
    ]
    
    # Compliance percentage
    if required_courses:
        compliance = (len(completed_course_ids) / len(required_courses)) * 100
    else:
        compliance = 100.0
    
    return TrainingStatusSummary(
        volunteer_id=volunteer_id,
        total_courses=len(trainings),
        completed_courses=len(completed_course_ids),
        expired_courses=expired_count,
        expiring_soon=expiring_soon,
        compliance_percentage=round(compliance, 2),
        missing_required=missing_required
    )


# =============== Certifications ===============

@router.get("/volunteers/{volunteer_id}/certifications", response_model=List[CertificationResponse])
def get_volunteer_certifications(
    volunteer_id: int,
    include_expired: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all certifications for a volunteer."""
    # Verify volunteer
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    query = db.query(Certification).filter(
        Certification.volunteer_id == volunteer_id
    )
    
    if not include_expired:
        query = query.filter(
            or_(
                Certification.expiration_date.is_(None),
                Certification.expiration_date >= date.today()
            )
        )
    
    certs = query.all()
    
    # Enhance with computed properties
    result = []
    for cert in certs:
        cert_dict = {
            **cert.__dict__,
            'is_expired': cert.is_expired,
            'days_until_expiration': cert.days_until_expiration
        }
        result.append(CertificationResponse(**cert_dict))
    
    return result


@router.post("/volunteers/{volunteer_id}/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def add_certification(
    volunteer_id: int,
    cert_data: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a certification for a volunteer."""
    # Verify volunteer
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.tenant_id == current_user.tenant_id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Create certification
    cert = Certification(**cert_data.dict())
    cert.verification_status = 'pending'
    cert.verified_by = current_user.id
    
    db.add(cert)
    db.commit()
    db.refresh(cert)
    
    return CertificationResponse(
        **cert.__dict__,
        is_expired=cert.is_expired,
        days_until_expiration=cert.days_until_expiration
    )


@router.patch("/certifications/{cert_id}", response_model=CertificationResponse)
def update_certification(
    cert_id: int,
    cert_data: CertificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a certification (e.g., verify, update expiration)."""
    cert = db.query(Certification).filter(Certification.id == cert_id).first()
    
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found"
        )
    
    # Update fields
    for field, value in cert_data.dict(exclude_unset=True).items():
        setattr(cert, field, value)
    
    if cert_data.verification_status:
        cert.verification_date = date.today()
        cert.verified_by = current_user.id
    
    db.commit()
    db.refresh(cert)
    
    return CertificationResponse(
        **cert.__dict__,
        is_expired=cert.is_expired,
        days_until_expiration=cert.days_until_expiration
    )


# =============== Reports ===============

@router.get("/reports/expiring", response_model=List[ExpiringTrainingReport])
def get_expiring_training_report(
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get report of training expiring within X days."""
    cutoff_date = date.today() + timedelta(days=days)
    
    # Query expiring training
    trainings = db.query(
        VolunteerTraining,
        Volunteer,
        TrainingCourse
    ).join(
        Volunteer, VolunteerTraining.volunteer_id == Volunteer.id
    ).join(
        TrainingCourse, VolunteerTraining.course_id == TrainingCourse.id
    ).filter(
        Volunteer.tenant_id == current_user.tenant_id,
        VolunteerTraining.expiration_date.isnot(None),
        VolunteerTraining.expiration_date <= cutoff_date,
        VolunteerTraining.expiration_date >= date.today()
    ).order_by(
        VolunteerTraining.expiration_date
    ).all()
    
    # Format results
    results = []
    for training, volunteer, course in trainings:
        days_remaining = (training.expiration_date - date.today()).days
        results.append(ExpiringTrainingReport(
            volunteer_id=volunteer.id,
            volunteer_name=volunteer.full_name,
            course_name=course.name,
            expiration_date=training.expiration_date,
            days_until_expiration=days_remaining,
            is_required=course.is_required
        ))
    
    return results


# =============== TRAIN Integration ===============

@router.post("/train/sync", response_model=TRAINSyncResponse)
async def sync_from_train(
    sync_request: TRAINSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync training records from TRAIN API.
    This is a simulated implementation for Phase 1.
    """
    records_synced = 0
    errors = []
    
    # Determine which volunteers to sync
    if sync_request.volunteer_id:
        volunteers = [db.query(Volunteer).filter(
            Volunteer.id == sync_request.volunteer_id,
            Volunteer.tenant_id == current_user.tenant_id
        ).first()]
        
        if not volunteers[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )
    else:
        # Sync all volunteers in tenant
        volunteers = db.query(Volunteer).filter(
            Volunteer.tenant_id == current_user.tenant_id,
            Volunteer.application_status == 'approved'
        ).limit(10).all()  # Limit for demo
    
    # Sync each volunteer
    for volunteer in volunteers:
        try:
            # Call TRAIN service (simulated)
            train_records = await train_service.sync_volunteer_training(volunteer.email)
            
            for record in train_records:
                # Find or create course
                course = db.query(TrainingCourse).filter(
                    TrainingCourse.train_course_id == record['train_course_id']
                ).first()
                
                if not course:
                    # Create course from TRAIN data
                    course = TrainingCourse(
                        tenant_id=current_user.tenant_id,
                        train_course_id=record['train_course_id'],
                        name=record['course_name'],
                        course_code=record.get('course_code'),
                        provider=record.get('course_provider'),
                        category=record.get('course_category'),
                        is_required=False
                    )
                    db.add(course)
                    db.flush()
                
                # Check if training record already exists
                existing = db.query(VolunteerTraining).filter(
                    VolunteerTraining.train_completion_id == record['train_completion_id']
                ).first()
                
                if existing and not sync_request.force:
                    continue  # Skip if already exists
                
                # Create or update training record
                if existing:
                    training = existing
                else:
                    training = VolunteerTraining(
                        volunteer_id=volunteer.id,
                        course_id=course.id,
                        train_completion_id=record['train_completion_id']
                    )
                
                training.completion_date = record['completion_date']
                training.expiration_date = record.get('expiration_date')
                training.score = record.get('score')
                training.certificate_url = record.get('certificate_url')
                training.synced_from_train = True
                training.last_sync_date = datetime.utcnow()
                training.status = 'active'
                
                if not existing:
                    db.add(training)
                
                records_synced += 1
            
        except Exception as e:
            errors.append(f"Error syncing {volunteer.email}: {str(e)}")
    
    db.commit()
    
    return TRAINSyncResponse(
        success=len(errors) == 0,
        records_synced=records_synced,
        errors=errors,
        message=f"Synced {records_synced} training records from TRAIN"
    )


@router.get("/train/status")
async def get_train_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get TRAIN integration status.
    Placeholder for Phase 1.
    """
    return {
        "status": "simulated",
        "message": "TRAIN integration is currently simulated. Will be implemented with real API in Phase 2",
        "api_url": "https://api.train.org/v1",
        "last_sync": None,
        "features": {
            "daily_sync": False,
            "course_mapping": True,
            "expiration_tracking": True
        }
    }