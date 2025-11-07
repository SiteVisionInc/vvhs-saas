"""
Volunteer model with comprehensive profile management.
FIXED: Matches actual database schema from 01_init.sql
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from database import Base


class VolunteerStatus(str, enum.Enum):
    """Volunteer application status from dashboard requirements."""
    APPROVED = "approved"
    PENDING = "pending"
    INCOMPLETE = "incomplete"
    WORKING = "working"
    REJECTED = "rejected"
    INACTIVE = "inactive"


class AccountStatus(str, enum.Enum):
    """Volunteer account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class MRCLevel(str, enum.Enum):
    """MRC Level classification."""
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


class Volunteer(Base):
    """
    Volunteer profile model.
    Core entity for the volunteer management system.
    FIXED to match actual database columns.
    """
    __tablename__ = "volunteers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Authentication (for volunteer portal)
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255))
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    
    # Contact Information
    phone_primary = Column(String(20))
    phone_secondary = Column(String(20))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(2), default="VA")
    zip_code = Column(String(10))
    
    # Emergency Contact
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(100))
    
    # Application Status
    application_status = Column(String(20), default='pending', index=True)
    account_status = Column(String(20), default='active')
    mrc_level = Column(String(20))
    
    # Profile Details (matching DB columns exactly)
    occupation = Column(String(100))
    employer = Column(String(255))
    skills = Column(Text)  # This is TEXT in DB, not professional_skills
    languages = Column(String(255))
    
    # Training and Credentials
    certifications = Column(Text)
    train_id = Column(String(100))
    train_data = Column(Text)
    
    # Availability
    availability = Column(Text)
    travel_distance = Column(Integer, default=25)
    
    # Background Check
    background_check_date = Column(Date)
    background_check_status = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime)
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="volunteers")
    event_assignments = relationship("EventAssignment", back_populates="volunteer")
    training_records = relationship("TrainingRecord", back_populates="volunteer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Volunteer(id={self.id}, name='{self.full_name}', status='{self.application_status}')>"
    
    @property
    def full_name(self):
        """Get volunteer's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    # Computed properties for compatibility
    @property
    def total_hours(self):
        """Calculate total hours from event assignments."""
        if not self.event_assignments:
            return 0
        return sum(a.hours_completed or 0 for a in self.event_assignments)
    
    @property
    def status(self):
        """Alias for application_status for compatibility."""
        return self.application_status