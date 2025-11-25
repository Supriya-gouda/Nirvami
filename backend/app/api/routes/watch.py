from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.services.watch_service import WatchService
from typing import Dict

router = APIRouter()

@router.post("/data")
async def post_watch_data(data: Dict, current_user_id: str = Depends(get_current_user_id)):
    """Receive Apple Watch data payload and store it."""
    try:
        result = WatchService.store_watch_data(current_user_id, data)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store watch data")

@router.get("/today")
async def get_today_watch_data(current_user_id: str = Depends(get_current_user_id)):
    """Return today's watch data for the authenticated user."""
    data = WatchService.get_today_watch_data(current_user_id)
    return data
