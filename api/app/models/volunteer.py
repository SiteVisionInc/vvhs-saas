"""
Volunteer model with comprehensive profile management.
Enhanced to match the new database schema with all fields.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Enum as SQLEnum, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from database import Base


class VolunteerStatus(str, enum.Enum):
    """Volunteer application status."""
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
    Volunteer profile model - Enhanced version.
    Matches the enhanced database schema with all comprehensive fields.
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
    
    # Professional Information
    occupation = Column(String(100))
    employer = Column(String(255))
    professional_skills = Column(Text)
    license_number = Column(String(100))
    license_type = Column(String(100))
    license_state = Column(String(2))
    license_expiration = Column(Date)
    
    # Skills and Languages
    skills = Column(Text)
    languages = Column(String(255))
    
    # Training and Credentials
    certifications = Column(Text)
    certification_info = Column(Text)
    train_id = Column(String(100))
    train_data = Column(Text)
    
    # Availability and Preferences
    availability = Column(Text)
    availability_info = Column(Text)
    travel_distance = Column(Integer, default=25)
    preferred_roles = Column(Text)
    assigned_groups = Column(Text)
    assigned_roles = Column(Text)
    
    # Metrics and Performance (stored directly now)
    total_hours = Column(DECIMAL(10, 2), default=0)
    alert_response_rate = Column(DECIMAL(5, 2), default=0)
    badges_earned = Column(Text)
    
    # Background Check
    background_check_date = Column(Date)
    background_check_status = Column(String(20))
    
    # Important Dates
    application_date = Column(DateTime, default=datetime.utcnow)
    approval_date = Column(DateTime)
    last_activity_date = Column(DateTime)
    
    # System Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime)  # Backward compatibility
    approved_at = Column(DateTime)    # Backward compatibility
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="volunteers")
    event_assignments = relationship("EventAssignment", back_populates="volunteer", lazy="dynamic")
    training_records = relationship("TrainingRecord", back_populates="volunteer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Volunteer(id={self.id}, name='{self.full_name}', status='{self.application_status}')>"
    
    @property
    def full_name(self):
        """Get volunteer's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def status(self):
        """Alias for application_status for compatibility."""
        return self.application_status
    
    @property
    def phone(self):
        """Primary phone for compatibility."""
        return self.phone_primary
    
    @property
    def hours_completed(self):
        """Alias for total_hours for compatibility."""
        return self.total_hours or 0