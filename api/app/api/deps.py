"""
Dependency injection for FastAPI endpoints.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from database import get_db
from core.security import decode_token
from core.permissions import has_permission, Permission
from models.user import User, UserRole
from schemas.auth import TokenData

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(
            user_id=user_id,
            username=payload.get("username"),
            tenant_id=payload.get("tenant_id"),
            role=payload.get("role")
        )
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
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
    
    Usage:
        @router.get("/", dependencies=[Depends(require_permission(Permission.VIEW_VOLUNTEERS))])
    """
    def permission_checker(current_user: User = Depends(get_current_user)):
        # Build user permissions dict for sub-unit staff
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
    
    Usage:
        @router.get("/", dependencies=[Depends(require_role([UserRole.SYSTEM_ADMIN]))])
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges"
            )
        return current_user
    
    return role_checker
