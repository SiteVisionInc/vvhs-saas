"""
Permission checking utilities for role-based access control.
Implements the permission model from requirements.
"""
from typing import List
from models.user import UserRole


class Permission:
    """Permission definitions matching requirements."""
    
    # System Administration
    MANAGE_TENANTS = "manage_tenants"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    
    # User Management
    VIEW_ALL_USERS = "view_all_users"
    MANAGE_USERS = "manage_users"
    
    # Volunteer Management
    VIEW_VOLUNTEERS = "view_volunteers"
    EDIT_VOLUNTEERS = "edit_volunteers"
    APPROVE_VOLUNTEERS = "approve_volunteers"
    
    # Event Management
    VIEW_EVENTS = "view_events"
    CREATE_EVENTS = "create_events"
    EDIT_EVENTS = "edit_events"
    DELETE_EVENTS = "delete_events"
    
    # Scheduling
    ASSIGN_SHIFTS = "assign_shifts"
    MANAGE_WAITLIST = "manage_waitlist"
    
    # Communication
    VIEW_ALERTS = "view_alerts"
    SEND_ALERTS = "send_alerts"
    
    # Transfers
    INITIATE_TRANSFERS = "initiate_transfers"
    APPROVE_TRANSFERS = "approve_transfers"
    
    # Reports
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"
    
    # Training
    VIEW_TRAINING = "view_training"
    EDIT_TRAINING = "edit_training"


# Role to permission mapping
ROLE_PERMISSIONS: dict[UserRole, List[str]] = {
    UserRole.SYSTEM_ADMIN: [
        # System admins have all permissions
        Permission.MANAGE_TENANTS,
        Permission.MANAGE_SYSTEM_SETTINGS,
        Permission.VIEW_ALL_USERS,
        Permission.MANAGE_USERS,
        Permission.VIEW_VOLUNTEERS,
        Permission.EDIT_VOLUNTEERS,
        Permission.APPROVE_VOLUNTEERS,
        Permission.VIEW_EVENTS,
        Permission.CREATE_EVENTS,
        Permission.EDIT_EVENTS,
        Permission.DELETE_EVENTS,
        Permission.ASSIGN_SHIFTS,
        Permission.MANAGE_WAITLIST,
        Permission.VIEW_ALERTS,
        Permission.SEND_ALERTS,
        Permission.INITIATE_TRANSFERS,
        Permission.APPROVE_TRANSFERS,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_DATA,
        Permission.VIEW_TRAINING,
        Permission.EDIT_TRAINING,
    ],
    UserRole.ORG_ADMIN: [
        # Org admins (Unit Coordinators) have full tenant-level access
        Permission.MANAGE_USERS,
        Permission.VIEW_VOLUNTEERS,
        Permission.EDIT_VOLUNTEERS,
        Permission.APPROVE_VOLUNTEERS,
        Permission.VIEW_EVENTS,
        Permission.CREATE_EVENTS,
        Permission.EDIT_EVENTS,
        Permission.DELETE_EVENTS,
        Permission.ASSIGN_SHIFTS,
        Permission.MANAGE_WAITLIST,
        Permission.VIEW_ALERTS,
        Permission.SEND_ALERTS,
        Permission.INITIATE_TRANSFERS,
        Permission.APPROVE_TRANSFERS,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_DATA,
        Permission.VIEW_TRAINING,
        Permission.EDIT_TRAINING,
    ],
    UserRole.COORDINATOR: [
        # Coordinators have management capabilities
        Permission.VIEW_VOLUNTEERS,
        Permission.EDIT_VOLUNTEERS,
        Permission.VIEW_EVENTS,
        Permission.CREATE_EVENTS,
        Permission.EDIT_EVENTS,
        Permission.ASSIGN_SHIFTS,
        Permission.MANAGE_WAITLIST,
        Permission.VIEW_ALERTS,
        Permission.SEND_ALERTS,
        Permission.VIEW_REPORTS,
        Permission.EXPORT_DATA,
        Permission.VIEW_TRAINING,
    ],
    UserRole.SUB_UNIT_STAFF: [
        # Sub-unit staff have view-only by default
        # Actual permissions set via user.can_* fields
        Permission.VIEW_VOLUNTEERS,
        Permission.VIEW_EVENTS,
        Permission.VIEW_ALERTS,
        Permission.VIEW_TRAINING,
    ],
    UserRole.VOLUNTEER: [
        # Volunteers have minimal permissions (for portal access)
        Permission.VIEW_EVENTS,
    ],
}


def has_permission(user_role: UserRole, permission: str, user_permissions: dict = None) -> bool:
    """
    Check if a user role has a specific permission.
    
    Args:
        user_role: User's role
        permission: Permission to check
        user_permissions: Optional dict of user-specific permissions (for sub-unit staff)
        
    Returns:
        True if user has permission, False otherwise
    """
    # Get base permissions for role
    base_permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    if permission in base_permissions:
        return True
    
    # Check user-specific permissions for sub-unit staff
    if user_role == UserRole.SUB_UNIT_STAFF and user_permissions:
        permission_map = {
            Permission.EDIT_VOLUNTEERS: user_permissions.get("can_edit_data", False),
            Permission.SEND_ALERTS: user_permissions.get("can_edit_alerts", False),
            Permission.INITIATE_TRANSFERS: user_permissions.get("can_initiate_transfers", False),
            Permission.APPROVE_TRANSFERS: user_permissions.get("can_approve_transfers", False),
            Permission.EXPORT_DATA: user_permissions.get("can_export_data", False),
        }
        return permission_map.get(permission, False)
    
    return False


def get_user_permissions(user_role: UserRole, user_permissions: dict = None) -> List[str]:
    """
    Get all permissions for a user.
    
    Args:
        user_role: User's role
        user_permissions: Optional dict of user-specific permissions
        
    Returns:
        List of permission strings
    """
    permissions = ROLE_PERMISSIONS.get(user_role, []).copy()
    
    # Add user-specific permissions for sub-unit staff
    if user_role == UserRole.SUB_UNIT_STAFF and user_permissions:
        if user_permissions.get("can_edit_data"):
            permissions.append(Permission.EDIT_VOLUNTEERS)
        if user_permissions.get("can_edit_alerts"):
            permissions.append(Permission.SEND_ALERTS)
        if user_permissions.get("can_initiate_transfers"):
            permissions.append(Permission.INITIATE_TRANSFERS)
        if user_permissions.get("can_approve_transfers"):
            permissions.append(Permission.APPROVE_TRANSFERS)
        if user_permissions.get("can_export_data"):
            permissions.append(Permission.EXPORT_DATA)
    
    return permissions
