"""
Notification Service - Handles in-app notifications
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for creating and managing in-app notifications"""
    
    def __init__(self):
        self.supabase = get_supabase(use_service_role=True)
    
    async def create_health_alert_notification(
        self,
        user_id: str,
        concerns: List[str],
        recommendations: List[str],
        risk_level: str = "medium"
    ) -> Optional[Dict[str, Any]]:
        """
        Create in-app notification for health concerns
        
        Args:
            user_id: User ID
            concerns: List of detected concerns
            recommendations: List of recommendations
            risk_level: Risk level (low, medium, high)
            
        Returns:
            Created notification data or None if failed
        """
        try:
            # Format notification data
            title = "⚠️ Health Alert Detected"
            if risk_level.lower() == "high":
                title = "🚨 Important Health Alert"
            elif risk_level.lower() == "low":
                title = "ℹ️ Health Notification"
            
            # Create message body
            message_parts = []
            
            if concerns:
                message_parts.append("Detected concerns:")
                for concern in concerns[:3]:  # Limit to 3 for readability
                    message_parts.append(f"• {concern}")
            
            if recommendations:
                if message_parts:
                    message_parts.append("")  # Empty line
                message_parts.append("Recommended actions:")
                for rec in recommendations[:3]:
                    message_parts.append(f"• {rec}")
            
            message = "\n".join(message_parts)
            
            # Create notification record
            notification_data = {
                "id": str(uuid4()),
                "user_id": user_id,
                "type": "health_alert",
                "title": title,
                "message": message,
                "data": {
                    "concerns": concerns,
                    "recommendations": recommendations,
                    "risk_level": risk_level,
                    "timestamp": datetime.now().isoformat()
                },
                "read": False,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table('notifications').insert(notification_data).execute()
            
            if result.data:
                logger.info(f"✅ Created health alert notification for user {user_id}")
                return result.data[0]
            else:
                logger.error(f"❌ Failed to create notification for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating health alert notification: {e}")
            return None
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a general notification
        
        Args:
            user_id: User ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data
            
        Returns:
            Created notification or None
        """
        try:
            notification_data = {
                "id": str(uuid4()),
                "user_id": user_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data or {},
                "read": False,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table('notifications').insert(notification_data).execute()
            
            if result.data:
                logger.info(f"✅ Created {notification_type} notification for user {user_id}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error creating notification: {e}")
            return None
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's notifications
        
        Args:
            user_id: User ID
            unread_only: If True, return only unread notifications
            limit: Maximum number of notifications
            
        Returns:
            List of notifications
        """
        try:
            query = self.supabase.table('notifications')\
                .select('*')\
                .eq('user_id', user_id)
            
            if unread_only:
                query = query.eq('read', False)
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"❌ Error fetching notifications: {e}")
            return []
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            result = self.supabase.table('notifications')\
                .update({"read": True, "read_at": datetime.now().isoformat()})\
                .eq('id', notification_id)\
                .eq('user_id', user_id)\
                .execute()
            
            return bool(result.data)
        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {e}")
            return False
    
    async def mark_all_as_read(self, user_id: str) -> bool:
        """Mark all user notifications as read"""
        try:
            result = self.supabase.table('notifications')\
                .update({"read": True, "read_at": datetime.now().isoformat()})\
                .eq('user_id', user_id)\
                .eq('read', False)\
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"❌ Error marking all notifications as read: {e}")
            return False


# Singleton instance
_notification_service = None

def get_notification_service() -> NotificationService:
    """Get the singleton notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
