"""Integration endpoints for external systems."""
from fastapi import APIRouter, Depends
from models.user import User
from api.deps import get_current_user
from services.train import train_service

router = APIRouter()

@router.get("/train/status")
async def get_train_status(current_user: User = Depends(get_current_user)):
    """
    Get TRAIN integration status.
    Placeholder for Phase 1.
    """
    # TODO: Implement actual TRAIN API integration
    return {
        "status": "placeholder",
        "message": "TRAIN integration will be implemented in Phase 2",
        "api_url": "https://api.train.org/v1",
        "last_sync": None,
        "features": {
            "daily_sync": False,
            "course_mapping": False,
            "expiration_tracking": False
        }
    }

@router.post("/train/sync/{volunteer_id}")
async def sync_volunteer_training(
    volunteer_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger TRAIN sync for a volunteer.
    Placeholder for Phase 1.
    """
    # TODO: Implement actual sync logic
    records = await train_service.sync_volunteer_training("volunteer@example.com")
    return {
        "message": "Sync triggered (placeholder)",
        "volunteer_id": volunteer_id,
        "records_found": len(records),
        "sample_records": records
    }
