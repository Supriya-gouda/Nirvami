"""Emotion detection routes."""
from fastapi import APIRouter, Depends, Request, HTTPException
from app.utils.auth import get_current_user_id
from app.utils.mock_data import get_mock_emotions
from app.utils.database import get_supabase
from app.models.schemas import EmotionDetectionResponse, EmotionLog, EmotionAggregate
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


class LogEmotionRequest(BaseModel):
    emotion: str
    intensity: int
    notes: Optional[str] = None
    detected_from: str = 'manual'


@router.post("/log")
async def log_emotion(
    data: LogEmotionRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Log an emotion entry for the user."""
    supabase = get_supabase()
    
    try:
        # Create emotion log entry matching schema: emotion_type, confidence, all_scores, source
        emotion_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user_id,
            "emotion_type": data.emotion,
            "confidence": data.intensity / 100.0,  # Convert intensity to 0-1 confidence
            "all_scores": {data.emotion: data.intensity / 100.0},
            "source": data.detected_from,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("emotion_logs").insert(emotion_data).execute()
        
        if result.data:
            logger.info(f"Emotion logged for user {current_user_id}: {data.emotion}")
            return result.data[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to log emotion")
            
    except Exception as e:
        logger.error(f"Error logging emotion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to log emotion: {str(e)}")


@router.get("/history")
async def get_emotion_logs(
    current_user_id: str = Depends(get_current_user_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: int = 7,
    limit: int = 100
):
    """Get emotion logs for user."""
    supabase = get_supabase()
    
    try:
        # Use start_date if provided, otherwise calculate from days
        if start_date:
            since_date = start_date
        else:
            since_date = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
        
        query = supabase.table("emotion_logs").select("*").eq(
            "user_id", current_user_id
        ).gte("created_at", since_date)
        
        # Add end_date filter if provided
        if end_date:
            # Add one day to include the entire end_date
            end_datetime = (datetime.fromisoformat(end_date) + timedelta(days=1)).isoformat()
            query = query.lt("created_at", end_datetime)
        
        result = query.order(
            "created_at", desc=True
        ).limit(limit).execute()
        
        logger.info(f"Retrieved {len(result.data)} emotion logs for user {current_user_id}")
        return result.data
    except Exception as e:
        logger.error(f"Error fetching emotion logs: {e}", exc_info=True)
        # Return empty array instead of crashing
        return []



@router.get("/aggregates", response_model=List[EmotionAggregate])
async def get_emotion_aggregates(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 30
):
    """Get daily emotion aggregates."""
    supabase = get_supabase()
    
    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = supabase.table("emotion_aggregates").select("*").eq(
            "user_id", current_user_id
        ).gte("date", since_date).order("date", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching aggregates: {e}")
        raise
