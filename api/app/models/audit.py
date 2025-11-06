"""
Audit logging model for compliance and security.
Tracks all significant user actions in the system.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class AuditLog(Base):
    """
    Audit log for tracking user actions.
    Required for compliance (HIPAA, security standards).
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User and Tenant
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)  # e.g., "user.created", "volunteer.updated"
    resource_type = Column(String(50), nullable=False)  # e.g., "volunteer", "event"
    resource_id = Column(Integer)
    
    # Request Information
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    endpoint = Column(String(255))
    http_method = Column(String(10))
    
    # Change Details
    old_values = Column(JSON)  # Previous state (for updates)
    new_values = Column(JSON)  # New state
    
    # Additional Context
    description = Column(Text)
    status = Column(String(20))  # success, failure, error
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"
