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


@router.get("/unread-count")
async def get_unread_count(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get count of unread notifications."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("notifications").select("id", count="exact").eq(
            "user_id", current_user_id
        ).eq("read", False).execute()
        
        return {"count": result.count or 0}
    except Exception as e:
        logger.error(f"Error fetching unread count: {e}")
        return {"count": 0}


@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Mark an alert as acknowledged."""
    supabase = get_supabase()
    
    try:
        from datetime import datetime
        
        result = supabase.table("alerts").update({
            "status": "acknowledged",
            "acknowledged_at": datetime.utcnow().isoformat()
        }).eq("id", alert_id).eq("user_id", current_user_id).execute()
        
        if result.data:
            logger.info(f"✅ Alert {alert_id} acknowledged by user {current_user_id}")
            return result.data[0]
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Alert not found")
            
    except Exception as e:
        logger.error(f"❌ Error acknowledging alert: {e}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Mark a notification as read."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("notifications").update({
            "read": True
        }).eq("id", notification_id).eq("user_id", current_user_id).execute()
        
        if result.data:
            logger.info(f"✅ Notification {notification_id} marked as read by user {current_user_id}")
            return result.data[0]
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except Exception as e:
        logger.error(f"❌ Error marking notification as read: {e}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

