"""
Event Assignment model for volunteer-event relationships.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class EventAssignment(Base):
    """
    Model for tracking volunteer assignments to events.
    """
    __tablename__ = "event_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    
    # Status - using string instead of enum for flexibility
    status = Column(String(20), nullable=False, default='pending')
    
    # Hours tracking
    hours_completed = Column(DECIMAL(5, 2))
    hours_served = Column(DECIMAL(5, 2))
    
    # Check-in/Check-out
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    coordinator_notes = Column(Text)
    volunteer_notes = Column(Text)
    
    # Timestamps
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="assignments")
    volunteer = relationship("Volunteer", back_populates="event_assignments")
    shift = relationship("Shift", back_populates="assignments", lazy="joined")
    
    __table_args__ = (
        UniqueConstraint('event_id', 'volunteer_id', 'shift_id', name='_event_volunteer_shift_uc'),
    )
    
    def __repr__(self):
        return f"<EventAssignment(id={self.id}, event={self.event_id}, volunteer={self.volunteer_id}, status='{self.status}')>"