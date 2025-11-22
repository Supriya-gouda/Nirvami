"""Wearable device integration routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import WearableDataRequest, WearableSnapshot
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/latest")
async def get_latest_wearable(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get latest wearable data for the user."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("wearable_snapshots").select("*").eq(
            "user_id", current_user_id
        ).order("recorded_at", desc=True).limit(1).execute()
        
        if result.data:
            return result.data[0]
        else:
            return None
    except Exception as e:
        logger.error(f"Error getting wearable data: {e}", exc_info=True)
        return None


@router.post("/push")
async def push_wearable_data(
    data: WearableDataRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Push wearable data from device."""
    supabase = get_supabase()
    
    try:
        # Handle recorded_at - convert to datetime if string
        recorded_at = data.recorded_at
        if recorded_at is None:
            recorded_at = datetime.utcnow()
        elif isinstance(recorded_at, str):
            from dateutil import parser
            recorded_at = parser.parse(recorded_at)
        
        wearable_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user_id,
            "recorded_at": recorded_at.isoformat() if hasattr(recorded_at, 'isoformat') else str(recorded_at),
            "device_type": data.device_type or "manual",
            "heart_rate": data.heart_rate,
            "hrv": data.hrv,
            "sleep_hours": data.sleep_hours,
            "sleep_quality": data.sleep_quality,
            "steps": data.steps,
            "active_calories": data.active_calories,
            "stress_level": data.stress_level,
            "raw_data": data.raw_data or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Saving wearable data: {wearable_data}")
        result = supabase.table("wearable_snapshots").insert(wearable_data).execute()
        
        if result.data:
            logger.info(f"✅ Wearable data saved for user {current_user_id}")
            return result.data[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to save wearable data")
            
    except Exception as e:
        logger.error(f"❌ Error pushing wearable data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save wearable data: {str(e)}")
