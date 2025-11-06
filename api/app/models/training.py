"""
Training and certification models.
Integrates with TRAIN API for course completion tracking.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class TrainingRecord(Base):
    """
    Training record for volunteers.
    Synced from TRAIN API daily (per requirements).
    """
    __tablename__ = "training_records"
    
    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False, index=True)
    
    # TRAIN Integration
    train_course_id = Column(String(100), index=True)  # External TRAIN course ID
    train_completion_id = Column(String(100), unique=True)  # Unique completion record
    
    # Course Information
    course_name = Column(String(255), nullable=False)
    course_category = Column(String(100))
    course_provider = Column(String(255))
    
    # Completion Details
    completion_date = Column(Date, nullable=False)
    expiration_date = Column(Date)
    ce_credits = Column(Integer, default=0)
    
    # Status
    is_expired = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)  # Required for certain roles/events
    
    # Sync Information
    synced_from_train = Column(Boolean, default=False)
    last_sync_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    volunteer = relationship("Volunteer", back_populates="training_records")
    
    def __repr__(self):
        return f"<TrainingRecord(id={self.id}, course='{self.course_name}', volunteer_id={self.volunteer_id})>"


class TrainingRequirement(Base):
    """
    Training requirements for events or roles.
    Used to restrict scheduling based on training compliance.
    """
    __tablename__ = "training_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Requirement Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    train_course_id = Column(String(100))  # Maps to TRAIN course
    
    # Applicability
    required_for_roles = Column(Text)  # JSON array of role names
    required_for_event_types = Column(Text)  # JSON array of event types
    
    # Validity
    validity_period_days = Column(Integer)  # Days before expiration
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<TrainingRequirement(id={self.id}, name='{self.name}')>"
