"""
Simplified dependency injection for FastAPI endpoints.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError
from sqlalchemy.orm import Session

from database import get_db
from core.security import decode_token
from core.permissions import has_permission, Permission
from models.user import User, UserRole
from schemas.auth import TokenData


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Simplified version that extracts token from Authorization header.
    """
    # Get Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )
    
    # Extract token (expecting "Bearer <token>")
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authorization header format"
        )
    
    # Decode token
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
            
        token_data = TokenData(
            user_id=user_id,
            username=payload.get("username"),
            tenant_id=payload.get("tenant_id"),
            role=payload.get("role")
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is not active (status: {user.status})"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active."""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission: str):
    """
    Dependency factory for permission checking.
    """
    def permission_checker(current_user: User = Depends(get_current_user)):
        user_permissions = {
            "can_edit_data": current_user.can_edit_data,
            "can_edit_alerts": current_user.can_edit_alerts,
            "can_initiate_transfers": current_user.can_initiate_transfers,
            "can_approve_transfers": current_user.can_approve_transfers,
            "can_export_data": current_user.can_export_data,
        }
        
        if not has_permission(current_user.role, permission, user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user
    
    return permission_checker


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency factory for role checking.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges"
            )
        return current_user
    
    return role_checker