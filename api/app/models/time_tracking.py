# api/app/models/time_tracking.py
"""
Time tracking models for volunteer hours.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class TimeEntry(Base):
    """
    Volunteer time entry/hours tracking.
    """
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    
    # Time tracking
    check_in_time = Column(DateTime, nullable=False)
    check_out_time = Column(DateTime)
    duration_minutes = Column(Integer)
    hours_decimal = Column(DECIMAL(5, 2))
    
    # Entry method
    entry_method = Column(String(50), nullable=False, default='manual')
    
    # Geolocation
    check_in_lat = Column(DECIMAL(10, 8))
    check_in_lng = Column(DECIMAL(11, 8))
    check_out_lat = Column(DECIMAL(10, 8))
    check_out_lng = Column(DECIMAL(11, 8))
    location_verified = Column(Boolean, default=False)
    
    # Approval workflow
    status = Column(String(50), nullable=False, default='pending', index=True)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Notes
    volunteer_notes = Column(Text)
    coordinator_notes = Column(Text)
    dispute_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    volunteer = relationship("Volunteer")
    event = relationship("Event")
    
    def calculate_duration(self):
        """Calculate duration in minutes and hours."""
        if self.check_out_time and self.check_in_time:
            delta = self.check_out_time - self.check_in_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            self.hours_decimal = round(self.duration_minutes / 60, 2)
    
    def __repr__(self):
        return f"<TimeEntry(id={self.id}, volunteer={self.volunteer_id}, hours={self.hours_decimal})>"


class EventQRCode(Base):
    """
    QR codes for event/shift check-in.
    """
    __tablename__ = "event_qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    
    # QR Code data
    qr_code_hash = Column(String(255), unique=True, nullable=False, index=True)
    qr_code_url = Column(String(500))
    
    # Validity
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    max_uses = Column(Integer)
    use_count = Column(Integer, default=0)
    
    # Configuration
    require_photo = Column(Boolean, default=False)
    require_signature = Column(Boolean, default=False)
    allow_early_checkin_minutes = Column(Integer, default=15)
    allow_late_checkout_minutes = Column(Integer, default=30)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship("Event")
    
    def is_valid(self) -> bool:
        """Check if QR code is currently valid."""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses and self.use_count >= self.max_uses:
            return False
        return True
    
    def __repr__(self):
        return f"<EventQRCode(id={self.id}, event={self.event_id}, hash='{self.qr_code_hash[:20]}...')>"


class CheckinSession(Base):
    """
    Active check-in sessions for mobile/kiosk.
    """
    __tablename__ = "checkin_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"))
    qr_code_id = Column(Integer, ForeignKey("event_qr_codes.id"))
    
    # Session data
    check_in_time = Column(DateTime, nullable=False)
    check_out_time = Column(DateTime)
    device_info = Column(Text)  # JSON string
    ip_address = Column(String(45))
    
    # Status
    status = Column(String(50), default='active')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    volunteer = relationship("Volunteer")
    event = relationship("Event")
    
    def __repr__(self):
        return f"<CheckinSession(id={self.id}, volunteer={self.volunteer_id}, status='{self.status}')>"