"""Alerts and notifications routes."""
from fastapi import APIRouter, Depends
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import Alert, Notification
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Alert])
async def get_alerts(
    current_user_id: str = Depends(get_current_user_id),
    status: str = "active"
):
    """Get user alerts."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("alerts").select("*").eq(
            "user_id", current_user_id
        ).eq("status", status).order("created_at", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise


@router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    current_user_id: str = Depends(get_current_user_id),
    unread_only: bool = False
):
    """Get user notifications."""
    supabase = get_supabase()
    
    try:
        query = supabase.table("notifications").select("*").eq("user_id", current_user_id)
        
        if unread_only:
            query = query.eq("read", False)
        
        result = query.order("created_at", desc=True).limit(50).execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise
