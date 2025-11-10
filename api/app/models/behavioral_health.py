"""
Behavioral Health module models.
Comprehensive clinical workflow system for managing behavioral health patient referrals and placements.
This is a SEPARATE subsystem from the volunteer management system.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, DECIMAL, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from database import Base


# ==================== ENUMS ====================

class RiskLevel(str, enum.Enum):
    """Patient risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReferralStatus(str, enum.Enum):
    """Referral workflow status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    PLACED = "placed"
    DISCHARGED = "discharged"
    CANCELLED = "cancelled"


class ReferralPriority(str, enum.Enum):
    """Referral priority level."""
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class PlacementOutcome(str, enum.Enum):
    """Discharge/placement outcome."""
    COMPLETED = "completed"
    TRANSFER = "transfer"
    AMA = "ama"  # Against Medical Advice
    DECEASED = "deceased"
    OTHER = "other"


class FacilityType(str, enum.Enum):
    """Facility classification."""
    HOSPITAL = "hospital"
    DETOX = "detox"
    RESIDENTIAL = "residential"
    OUTPATIENT = "outpatient"
    CRISIS = "crisis"
    OTHER = "other"


class BedType(str, enum.Enum):
    """Bed/unit classification."""
    GENERAL = "general"
    ADOLESCENT = "adolescent"
    GERIATRIC = "geriatric"
    SUD = "sud"  # Substance Use Disorder
    DETOX = "detox"
    CRISIS = "crisis"


# ==================== MODELS ====================

class BHPatient(Base):
    """
    Behavioral Health Patient model.
    Contains PHI - must be encrypted and access-controlled.
    """
    __tablename__ = "bh_patients"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Medical Record Number (optional - may not exist for new patients)
    mrn = Column(String(100), index=True)
    
    # Demographics (PHI - ENCRYPTED)
    first_name = Column(String(100), nullable=False)  # Should be encrypted in production
    last_name = Column(String(100), nullable=False)   # Should be encrypted in production
    dob = Column(Date)  # Should be encrypted in production
    gender = Column(String(50))
    
    # Contact Information (JSONB for flexibility)
    # Format: [{"type": "guardian", "name": "...", "phone": "...", "relationship": "..."}]
    guardians = Column(JSONB)
    
    # Format: [{"type": "home", "line1": "...", "city": "...", "state": "...", "zip": "..."}]
    addresses = Column(JSONB)
    
    # Format: [{"type": "mobile", "number": "...", "preferred": true}]
    phones = Column(JSONB)
    
    # Format: [{"name": "...", "phone": "...", "relationship": "..."}]
    emergency_contacts = Column(JSONB)
    
    # Consent Flags
    # Format: {"treatment": true, "release_info": false, "research": false}
    consent_flags = Column(JSONB)
    
    # Clinical Information
    risk_level = Column(String(50), default=RiskLevel.LOW.value)
    
    # Clinical notes (ENCRYPTED)
    notes = Column(Text)  # Should be encrypted in production
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    screenings = relationship("BHScreening", back_populates="patient", cascade="all, delete-orphan")
    referrals = relationship("BHReferral", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BHPatient(id={self.id}, mrn='{self.mrn}', risk='{self.risk_level}')>"


class BHScreening(Base):
    """
    Clinical screening/assessment results.
    Supports multiple instruments: C-SSRS, ASAM, PHQ-9, etc.
    """
    __tablename__ = "bh_screenings"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("bh_patients.id"), nullable=False, index=True)
    
    # Screening Instrument
    instrument_type = Column(String(100), nullable=False)  # 'C-SSRS', 'ASAM', 'PHQ-9', etc.
    
    # Score/Results
    score = Column(DECIMAL(5, 2))  # Primary score
    
    # Detailed results as JSON
    # Format depends on instrument:
    # C-SSRS: {"ideation": {...}, "behavior": {...}, "severity": 4}
    # ASAM: {"dimension1": {...}, "dimension2": {...}, "recommended_level": "3.5"}
    # PHQ-9: {"q1": 2, "q2": 1, ..., "total": 15, "severity": "moderate"}
    details_json = Column(JSONB)
    
    # Clinician Information
    clinician_id = Column(Integer, ForeignKey("bh_users.id"), nullable=False)
    screening_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    patient = relationship("BHPatient", back_populates="screenings")
    clinician = relationship("BHUser", foreign_keys=[clinician_id])
    
    def __repr__(self):
        return f"<BHScreening(id={self.id}, instrument='{self.instrument_type}', score={self.score})>"


class BHFacility(Base):
    """
    Behavioral health treatment facilities.
    Includes hospitals, detox centers, residential facilities, etc.
    """
    __tablename__ = "bh_facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Facility Information
    name = Column(String(255), nullable=False, index=True)
    facility_type = Column(String(100), nullable=False)  # hospital, detox, residential, etc.
    region_id = Column(Integer)  # Geographic region for filtering
    
    # Capabilities (JSONB array)
    # Format: ["adolescent", "geriatric", "SUD", "detox", "dual_diagnosis"]
    capabilities = Column(JSONB)
    
    # Contact Information
    contact_name = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    
    # Address (JSONB)
    # Format: {"line1": "...", "city": "...", "state": "...", "zip": "..."}
    address = Column(JSONB)
    
    # Integration
    emr_id = Column(String(100))  # External EHR system ID for automated feeds
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bed_snapshots = relationship("BHBedSnapshot", back_populates="facility", cascade="all, delete-orphan")
    placements = relationship("BHPlacement", back_populates="facility")
    
    def __repr__(self):
        return f"<BHFacility(id={self.id}, name='{self.name}', type='{self.facility_type}')>"


class BHBedSnapshot(Base):
    """
    Real-time bed availability snapshot.
    Updated daily by facility coordinators or automated EHR feeds.
    """
    __tablename__ = "bh_bed_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("bh_facilities.id"), nullable=False, index=True)
    
    # Unit/Bed Type
    unit_name = Column(String(100))
    bed_type = Column(String(100), nullable=False)  # general, adolescent, geriatric, SUD, detox
    
    # Capacity
    capacity_total = Column(Integer, nullable=False)
    capacity_available = Column(Integer, nullable=False)
    
    # Last Update
    last_reported_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    reported_by = Column(Integer, ForeignKey("bh_users.id"))
    
    # Constraints/Requirements (JSONB)
    # Format: {"age_min": 12, "age_max": 17, "gender": "F", "insurance": ["medicaid", "medicare"]}
    constraints = Column(JSONB)
    
    # Relationships
    facility = relationship("BHFacility", back_populates="bed_snapshots")
    reporter = relationship("BHUser", foreign_keys=[reported_by])
    
    def __repr__(self):
        return f"<BHBedSnapshot(id={self.id}, facility={self.facility_id}, available={self.capacity_available}/{self.capacity_total})>"
    
    @property
    def is_stale(self) -> bool:
        """Check if bed data is stale (>24 hours old)."""
        if not self.last_reported_at:
            return True
        hours_old = (datetime.utcnow() - self.last_reported_at).total_seconds() / 3600
        return hours_old > 24


class BHReferral(Base):
    """
    Patient referral for behavioral health placement.
    Central workflow object coordinating intake → placement → discharge.
    """
    __tablename__ = "bh_referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("bh_patients.id"), nullable=False, index=True)
    
    # Referrer Information
    created_by = Column(Integer, ForeignKey("bh_users.id"), nullable=False)  # Clinician/referrer
    region_id = Column(Integer)  # Geographic region
    
    # Workflow Status
    status = Column(String(50), nullable=False, default=ReferralStatus.DRAFT.value, index=True)
    priority = Column(String(50), nullable=False, default=ReferralPriority.ROUTINE.value)
    
    # Important Dates
    referral_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    placement_date = Column(DateTime, index=True)
    discharge_date = Column(DateTime, index=True)
    
    # Supporting Documents (JSONB array of S3 URLs)
    # Format: [{"type": "treatment_history", "url": "s3://...", "uploaded_at": "..."}]
    attachments = Column(JSONB)
    
    # Clinical Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("BHPatient", back_populates="referrals")
    referrer = relationship("BHUser", foreign_keys=[created_by])
    placements = relationship("BHPlacement", back_populates="referral", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BHReferral(id={self.id}, patient={self.patient_id}, status='{self.status}')>"


class BHPlacement(Base):
    """
    Actual patient placement at a facility.
    Links referral → facility with admission/discharge details.
    """
    __tablename__ = "bh_placements"
    
    id = Column(Integer, primary_key=True, index=True)
    referral_id = Column(Integer, ForeignKey("bh_referrals.id"), nullable=False, index=True)
    facility_id = Column(Integer, ForeignKey("bh_facilities.id"), nullable=False, index=True)
    
    # Placement Details
    bed_type = Column(String(100), nullable=False)
    
    # Decision Information
    decision_by = Column(Integer, ForeignKey("bh_users.id"), nullable=False)  # Facility coordinator
    decision_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Admission/Discharge
    admission_date = Column(DateTime, index=True)
    discharge_date = Column(DateTime, index=True)
    
    # Transport Details (JSONB)
    # Format: {"method": "ambulance", "company": "...", "eta": "...", "notes": "..."}
    transport_details = Column(JSONB)
    
    # Outcome Tracking
    outcome = Column(String(100))  # completed, transfer, AMA, etc.
    length_of_stay = Column(Integer)  # Days
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referral = relationship("BHReferral", back_populates="placements")
    facility = relationship("BHFacility", back_populates="placements")
    decision_maker = relationship("BHUser", foreign_keys=[decision_by])
    
    def __repr__(self):
        return f"<BHPlacement(id={self.id}, referral={self.referral_id}, facility={self.facility_id})>"


class BHUser(Base):
    """
    Behavioral Health system users.
    Links to base User model but adds BH-specific roles and credentials.
    """
    __tablename__ = "bh_users"
    
    id = Column(Integer, primary_key=True, index=True)
    base_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # BH-Specific Role
    # clinician, facility_coordinator, mobile_crisis, peer_recovery, case_manager
    role = Column(String(100), nullable=False)
    
    # Professional Credentials
    npi = Column(String(20))  # National Provider Identifier
    license_number = Column(String(50))
    license_type = Column(String(50))  # MD, LCSW, RN, etc.
    
    # Specializations (JSONB array)
    # Format: ["adolescent", "geriatric", "SUD", "trauma"]
    specializations = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    base_user = relationship("User", foreign_keys=[base_user_id])
    
    def __repr__(self):
        return f"<BHUser(id={self.id}, role='{self.role}', npi='{self.npi}')>"


class BHFollowUp(Base):
    """
    Post-discharge follow-up tracking.
    Peer recovery specialists track outcomes at 30/60/90 days.
    """
    __tablename__ = "bh_followups"
    
    id = Column(Integer, primary_key=True, index=True)
    placement_id = Column(Integer, ForeignKey("bh_placements.id"), nullable=False, index=True)
    
    # Follow-up Schedule
    scheduled_date = Column(Date, nullable=False, index=True)
    followup_type = Column(String(50))  # day_30, day_60, day_90
    
    # Assigned Specialist
    assigned_to = Column(Integer, ForeignKey("bh_users.id"))
    
    # Completion
    completed_date = Column(Date)
    completed_by = Column(Integer, ForeignKey("bh_users.id"))
    
    # Outcome Data (JSONB)
    # Format: {"status": "stable", "housing": "stable", "employment": "seeking", "notes": "..."}
    outcome_data = Column(JSONB)
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, completed, missed, declined
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    placement = relationship("BHPlacement")
    specialist = relationship("BHUser", foreign_keys=[assigned_to])
    completed_by_user = relationship("BHUser", foreign_keys=[completed_by])
    
    def __repr__(self):
        return f"<BHFollowUp(id={self.id}, placement={self.placement_id}, type='{self.followup_type}')>"
