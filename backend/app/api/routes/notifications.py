"""Notification routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.services.notification_service import get_notification_service
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
notification_service = get_notification_service()


@router.get("")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    """Get user notifications"""
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=current_user_id,
            unread_only=unread_only,
            limit=limit
        )
        return notifications
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Mark notification as read"""
    try:
        success = await notification_service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user_id
        )
        
        if success:
            return {"success": True, "message": "Notification marked as read"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")


@router.post("/read-all")
async def mark_all_read(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Mark all notifications as read"""
    try:
        success = await notification_service.mark_all_as_read(user_id=current_user_id)
        
        if success:
            return {"success": True, "message": "All notifications marked as read"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark all as read")
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark all as read")
