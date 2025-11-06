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
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    response_name = Column(String(255))  # e.g., "COVID-19 Response"
    mission_types = Column(Text)  # JSON array: ["Behavioral Health/Resiliency", "Infection Prevention Education"]
    requestor_type = Column(String(100))
    
    # Visibility and Configuration
    visible_to_volunteers = Column(Boolean, default=True)
    allow_self_signup = Column(Boolean, default=False)  # Sign-Up Genius feature
    enable_waitlist = Column(Boolean, default=False)  # New from requirements
    districts = Column(Text)  # JSON array of district names
    
    # Status
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.DRAFT)
    
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
    is_overnight = Column(Boolean, default=False)
    
    # Capacity
    slots_total = Column(Integer, nullable=False, default=1)
    slots_filled = Column(Integer, default=0)
    
    # Requirements
    required_training = Column(Text)  # JSON array of required training IDs
    required_certifications = Column(Text)  # JSON array
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="shifts")
    assignments = relationship("EventAssignment", back_populates="shift")
    
    @property
    def is_full(self):
        """Check if shift is at capacity."""
        return self.slots_filled >= self.slots_total
    
    def __repr__(self):
        return f"<Shift(id={self.id}, name='{self.name}', slots={self.slots_filled}/{self.slots_total})>"


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
    status = Column(SQLEnum(AssignmentStatus), nullable=False, default=AssignmentStatus.PENDING)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    
    # Time Tracking
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    hours_served = Column(Integer, default=0)
    
    # Notes
    coordinator_notes = Column(Text)
    volunteer_notes = Column(Text)
    
    # Timestamps
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="assignments")
    shift = relationship("Shift", back_populates="assignments")
    volunteer = relationship("Volunteer", back_populates="event_assignments")
    
    def __repr__(self):
        return f"<EventAssignment(id={self.id}, volunteer_id={self.volunteer_id}, status='{self.status}')>"
