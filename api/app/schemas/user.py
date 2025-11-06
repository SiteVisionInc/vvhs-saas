"""
User schemas for staff and administrator management.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    role: UserRole = UserRole.SUB_UNIT_STAFF


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    tenant_id: int
    
    # Sub-unit staff permissions (radio buttons from requirements)
    can_view_data: bool = True
    can_edit_data: bool = False
    can_send_password_reminder: bool = False
    can_initiate_transfers: bool = False
    can_approve_transfers: bool = False
    can_view_alerts: bool = True
    can_edit_alerts: bool = False
    can_export_data: bool = False


class UserUpdate(BaseModel):
    """Schema for updating user."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    
    # Permissions
    can_view_data: Optional[bool] = None
    can_edit_data: Optional[bool] = None
    can_send_password_reminder: Optional[bool] = None
    can_initiate_transfers: Optional[bool] = None
    can_approve_transfers: Optional[bool] = None
    can_view_alerts: Optional[bool] = None
    can_edit_alerts: Optional[bool] = None
    can_export_data: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    tenant_id: int
    status: UserStatus
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    # Permissions
    can_view_data: bool
    can_edit_data: bool
    can_send_password_reminder: bool
    can_initiate_transfers: bool
    can_approve_transfers: bool
    can_view_alerts: bool
    can_edit_alerts: bool
    can_export_data: bool
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response."""
    total: int
    items: list[UserResponse]
