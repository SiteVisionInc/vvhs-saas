"""Event management endpoints (stub for Phase 1)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from api.deps import get_current_user

router = APIRouter()

@router.get("/")
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List events (stub)."""
    return {"message": "Events endpoint - coming soon", "items": []}

# TODO: Add event CRUD endpoints
