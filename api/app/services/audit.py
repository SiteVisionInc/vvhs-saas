"""
Audit logging service for tracking user actions.
"""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from models.audit import AuditLog


def log_action(
    db: Session,
    user_id: int,
    tenant_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    description: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success"
):
    """
    Create an audit log entry.
    
    Args:
        db: Database session
        user_id: ID of user performing action
        tenant_id: Tenant ID
        action: Action name (e.g., "volunteer.created")
        resource_type: Type of resource (e.g., "volunteer")
        resource_id: ID of affected resource
        description: Human-readable description
        old_values: Previous state (for updates)
        new_values: New state
        ip_address: Client IP address
        user_agent: Client user agent
        status: Action status (success, failure, error)
    """
    audit_log = AuditLog(
        user_id=user_id,
        tenant_id=tenant_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        created_at=datetime.utcnow()
    )
    
    db.add(audit_log)
    db.commit()
    
    return audit_log
