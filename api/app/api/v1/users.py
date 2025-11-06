"""User management endpoints (stub for Phase 1)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from api.deps import get_current_user
from schemas.user import UserListResponse, UserResponse

router = APIRouter()

# Add this endpoint to the users router
@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user


@router.get("/", response_model=UserListResponse)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List users in current tenant."""
    users = db.query(User).filter(User.tenant_id == current_user.tenant_id).offset(skip).limit(limit).all()
    total = db.query(User).filter(User.tenant_id == current_user.tenant_id).count()
    return UserListResponse(total=total, items=users)

# TODO: Add CRUD endpoints for users
