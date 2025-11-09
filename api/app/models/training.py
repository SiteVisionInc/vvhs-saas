# api/app/models/training.py
"""
Training and certification models.
Integrates with TRAIN API for course completion tracking.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime, date
from database import Base


class TrainingCourse(Base):
    """
    Training course catalog including TRAIN courses.
    """
    __tablename__ = "training_courses"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # TRAIN Integration
    train_course_id = Column(String(100), unique=True, index=True)
    
    # Course Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    course_code = Column(String(50))
    provider = Column(String(255))
    category = Column(String(100))
    
    # Requirements
    is_required = Column(Boolean, default=False)
    validity_period_days = Column(Integer)  # NULL = no expiration
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    training_records = relationship("VolunteerTraining", back_populates="course")
    
    def __repr__(self):
        return f"<TrainingCourse(id={self.id}, name='{self.name}')>"


class VolunteerTraining(Base):
    """
    Training completion record for volunteers.
    Synced from TRAIN API daily.
    """
    __tablename__ = "volunteer_training"
    
    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("training_courses.id"), nullable=False)
    
    # Completion Details
    completion_date = Column(Date, nullable=False)
    expiration_date = Column(Date)
    score = Column(DECIMAL(5, 2))
    certificate_number = Column(String(100))
    certificate_url = Column(String(500))
    
    # TRAIN Sync
    train_completion_id = Column(String(100), unique=True)
    synced_from_train = Column(Boolean, default=False)
    last_sync_date = Column(DateTime)
    
    # Status
    status = Column(String(50), default='active')  # active, expired, revoked
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    volunteer = relationship("Volunteer", back_populates="training_records")
    course = relationship("TrainingCourse", back_populates="training_records")
    
    @property
    def is_expired(self) -> bool:
        """Check if training has expired."""
        if not self.expiration_date:
            return False
        return self.expiration_date < date.today()
    
    def __repr__(self):
        return f"<VolunteerTraining(id={self.id}, volunteer={self.volunteer_id}, course={self.course_id})>"


class Certification(Base):
    """
    Professional licenses and certifications.
    Separate from training courses (e.g., RN license, EMT certification).
    """
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False, index=True)
    
    # Certification Details
    certification_type = Column(String(100), nullable=False)
    license_number = Column(String(100))
    issuing_authority = Column(String(255))
    
    # Dates
    issue_date = Column(Date)
    expiration_date = Column(Date)
    
    # Verification
    verification_status = Column(String(50), default='pending')
    verification_date = Column(Date)
    verification_method = Column(String(100))
    verified_by = Column(Integer, ForeignKey("users.id"))
    
    # Document
    document_url = Column(String(500))
    document_type = Column(String(50))
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    volunteer = relationship("Volunteer")
    
    @property
    def is_expired(self) -> bool:
        """Check if certification has expired."""
        if not self.expiration_date:
            return False
        return self.expiration_date < date.today()
    
    @property
    def days_until_expiration(self) -> int:
        """Get days until expiration."""
        if not self.expiration_date:
            return 999999
        delta = self.expiration_date - date.today()
        return delta.days
    
    def __repr__(self):
        return f"<Certification(id={self.id}, type='{self.certification_type}', volunteer={self.volunteer_id})>"


class TrainingRequirement(Base):
    """
    Training requirements for events or roles.
    Used to restrict scheduling based on training compliance.
    """
    __tablename__ = "training_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Requirement Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Linked Course
    course_id = Column(Integer, ForeignKey("training_courses.id"))
    
    # Applicability
    required_for_roles = Column(Text)  # JSON array
    required_for_event_types = Column(Text)  # JSON array
    
    # Grace Period
    grace_period_days = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TrainingRequirement(id={self.id}, name='{self.name}')>"