"""
Volunteer model with comprehensive profile management.
Supports application workflow and status tracking.
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
    application_status = Column(
        SQLEnum(VolunteerStatus), 
        nullable=False, 
        default=VolunteerStatus.INCOMPLETE,
        index=True
    )
    account_status = Column(
        SQLEnum(AccountStatus),
        nullable=False,
        default=AccountStatus.ACTIVE
    )
    mrc_level = Column(SQLEnum(MRCLevel), default=MRCLevel.LEVEL_1)
    
    # Professional Information
    occupation = Column(String(255))
    employer = Column(String(255))
    professional_skills = Column(Text)  # JSON array of skills
    
    # Credentials and Licenses
    license_number = Column(String(100))
    license_type = Column(String(100))
    license_state = Column(String(2))
    license_expiration = Column(Date)
    certification_info = Column(Text)  # JSON for multiple certifications
    
    # Availability and Preferences
    availability_info = Column(Text)  # JSON for availability schedule
    preferred_roles = Column(Text)  # JSON array of preferred roles
    
    # Groups and Roles (from requirements)
    assigned_groups = Column(Text)  # JSON array: ["Current Responders", "Emergency Response Volunteers"]
    assigned_roles = Column(Text)   # JSON array: ["General Support", "Medical Support"]
    
    # Engagement Metrics
    total_hours = Column(Integer, default=0)
    alert_response_rate = Column(Integer, default=0)  # Percentage
    badges_earned = Column(Text)  # JSON array of badge objects
    
    # Dates
    application_date = Column(DateTime, default=datetime.utcnow)
    approval_date = Column(DateTime)
    last_activity_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="volunteers")
    event_assignments = relationship("EventAssignment", back_populates="volunteer")
    training_records = relationship("TrainingRecord", back_populates="volunteer")
    
    def __repr__(self):
        return f"<Volunteer(id={self.id}, name='{self.full_name}', status='{self.application_status}')>"
    
    @property
    def full_name(self):
        """Get volunteer's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
