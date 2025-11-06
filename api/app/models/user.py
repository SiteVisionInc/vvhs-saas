"""
User model for staff and administrators.
Implements role-based access control (RBAC).
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration matching the requirements."""
    SYSTEM_ADMIN = "system_admin"           # State-level users, full system access
    ORG_ADMIN = "org_admin"                 # Local-level users (Unit Coordinators)
    COORDINATOR = "coordinator"              # Unit Coordinators with management access
    SUB_UNIT_STAFF = "sub_unit_staff"       # Local-level users with limited permissions
    VOLUNTEER = "volunteer"                  # Volunteer users (for portal access)


class UserStatus(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """
    User model for staff members and administrators.
    Separate from Volunteer model as staff have different access patterns.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Authentication
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    
    # Role and permissions
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.SUB_UNIT_STAFF)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    
    # Sub-unit staff permissions (as radio buttons in requirements)
    can_view_data = Column(Boolean, default=True)
    can_edit_data = Column(Boolean, default=False)
    can_send_password_reminder = Column(Boolean, default=False)
    can_initiate_transfers = Column(Boolean, default=False)
    can_approve_transfers = Column(Boolean, default=False)
    can_view_alerts = Column(Boolean, default=True)
    can_edit_alerts = Column(Boolean, default=False)
    can_export_data = Column(Boolean, default=False)
    
    # Multi-factor authentication
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    
    # Timestamps
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
