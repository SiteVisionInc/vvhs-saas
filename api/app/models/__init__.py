# api/app/models/__init__.py
"""
Models package initialization.
Imports all models for Alembic auto-generation.
"""
from models.tenant import Tenant
from models.user import User, UserRole, UserStatus
from models.volunteer import Volunteer, VolunteerStatus, AccountStatus, MRCLevel
from models.event import Event, Shift, EventAssignment, ActivityType, EventStatus, AssignmentStatus
from models.training import (
    TrainingCourse,
    VolunteerTraining,
    Certification,
    TrainingRequirement
)
from models.audit import AuditLog
from models.time_tracking import TimeEntry, EventQRCode, CheckinSession
from models.document import (
    PolicyDocument,
    ElectronicSignature,
    VolunteerDocument,
    DocumentAccessLog
)

__all__ = [
    "Tenant",
    "User",
    "UserRole",
    "UserStatus",
    "Volunteer",
    "VolunteerStatus",
    "AccountStatus",
    "MRCLevel",
    "Event",
    "Shift",
    "EventAssignment",
    "ActivityType",
    "EventStatus",
    "AssignmentStatus",
    "TrainingCourse",
    "VolunteerTraining",
    "Certification",
    "TrainingRequirement",
    "AuditLog",
    "TimeEntry",
    "EventQRCode",
    "CheckinSession",
    "PolicyDocument",
    "ElectronicSignature",
    "VolunteerDocument",
    "DocumentAccessLog",
]