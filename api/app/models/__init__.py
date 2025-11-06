"""
Models package initialization.
Imports all models for Alembic auto-generation.
"""
from models.tenant import Tenant
from models.user import User, UserRole, UserStatus
from models.volunteer import Volunteer, VolunteerStatus, AccountStatus, MRCLevel
from models.event import Event, Shift, EventAssignment, ActivityType, EventStatus, AssignmentStatus
from models.training import TrainingRecord, TrainingRequirement
from models.audit import AuditLog

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
    "TrainingRecord",
    "TrainingRequirement",
    "AuditLog",
]
