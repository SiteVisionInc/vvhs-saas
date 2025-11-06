"""Reporting endpoints (stub for Phase 1)."""
from fastapi import APIRouter, Depends
from models.user import User
from api.deps import get_current_user

router = APIRouter()

@router.get("/alert-response-rate")
def get_alert_response_report(current_user: User = Depends(get_current_user)):
    """Alert response rate report (stub)."""
    return {"message": "Alert response rate report - coming soon"}

# TODO: Add reporting endpoints
