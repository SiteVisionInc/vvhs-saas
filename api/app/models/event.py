"""
Event and shift management models.
Supports both emergency and non-emergency activities.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class ActivityType(str, enum.Enum):
    """Event activity type from requirements."""
    EMERGENCY = "emergency"
    NON_EMERGENCY = "non_emergency"
    # Note: This enum is kept for backward compatibility but not used in the model
    # The database column uses VARCHAR(50) to allow flexible activity types


class EventStatus(str, enum.Enum):
    """Event status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssignmentStatus(str, enum.Enum):
    """Volunteer assignment status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    WAITLIST = "waitlist"  # New from requirements


class Event(Base):
    """
    Event model for volunteer opportunities and deployments.
    Supports both scheduled and emergency events.
    """
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    staff_description = Column(Text)  # Description for coordinators
    volunteer_description = Column(Text)  # Description volunteers see
    location = Column(String(255))
    locality = Column(String(100))  # District/locality
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # Event Classification
    activity_type = Column(String(50), nullable=False)  # Changed from SQLEnum to String to match database VARCHAR(50)
    response_name = Column(String(255))  # e.g., "COVID-19 Response"
    mission_types = Column(Text)  # JSON array: ["Behavioral Health/Resiliency", "Infection Prevention Education"]
    requestor_type = Column(String(100))
    
    # Visibility and Configuration
    visible_to_volunteers = Column(Boolean, default=True)
    allow_self_signup = Column(Boolean, default=False)  # Sign-Up Genius feature
    enable_waitlist = Column(Boolean, default=False)  # New from requirements
    districts = Column(Text)  # JSON array of district names
    
    # Status
    status = Column(String(20), nullable=False, default='draft')  # Changed from SQLEnum to String to match database VARCHAR(20)
    
    # Impact Tracking (from requirements)
    impact_data = Column(Text)  # JSON: {"vaccines_administered": 150, "screenings": 75}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="events")
    shifts = relationship("Shift", back_populates="event", cascade="all, delete-orphan")
    assignments = relationship("EventAssignment", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', type='{self.activity_type}')>"


class Shift(Base):
    """
    Shift model for scheduled volunteer time blocks.
    Supports drag-and-drop creation and recurring templates.
    """
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    
    # Shift Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Capacity
    max_volunteers = Column(Integer)
    min_volunteers = Column(Integer, default=1)
    
    # Requirements
    required_skills = Column(Text)
    location = Column(String(255))
    
    # Advanced scheduling features (ADD THESE IF MISSING)
    allow_self_signup = Column(Boolean, default=False)
    enable_waitlist = Column(Boolean, default=True)
    waitlist_capacity = Column(Integer, default=10)
    conflict_detection = Column(Boolean, default=True)
    template_id = Column(Integer, ForeignKey("shift_templates.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="shifts")
    assignments = relationship("EventAssignment", back_populates="shift")
    
    def __repr__(self):
        return f"<Shift(id={self.id}, name='{self.name}')>"


class EventAssignment(Base):
    """
    Junction table for volunteer event assignments.
    Tracks who is assigned to which shift/event.
    """
    __tablename__ = "event_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False, index=True)
    
    # Assignment Details
    status = Column(String(20), nullable=False, default='pending')  # Changed from SQLEnum to String
    assigned_by = Column(Integer, ForeignKey("users.id"))
    
    # Time Tracking
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    hours_completed = Column(Integer, default=0)
    hours_served = Column(Integer, default=0)
    
    # Notes
    notes = Column(Text)
    coordinator_notes = Column(Text)
    volunteer_notes = Column(Text)
    
    # Timestamps
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="assignments")
    shift = relationship("Shift", back_populates="assignments")
    volunteer = relationship("Volunteer", back_populates="event_assignments")
    
    def __repr__(self):
        return f"<EventAssignment(id={self.id}, volunteer_id={self.volunteer_id}, status='{self.status}')>"