"""Clean Wearable API Routes - Simplified version."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.services.wearable_service_v2 import WearableService
from app.services.alert_service import AlertService
from app.utils.database import get_supabase
from pydantic import BaseModel
from typing import Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


class ManualEntryRequest(BaseModel):
    """Manual health entry from frontend."""
    date: str
    sleep_hours: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    steps: Optional[int] = None
    stress_level: Optional[int] = None
    calories_burned: Optional[float] = None
    hrv_ms: Optional[int] = None


@router.post("/manual-entry")
async def save_manual_entry(
    data: ManualEntryRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Save manually entered health data."""
    try:
        logger.info(f"📝 Manual entry from user {current_user_id}: {data.dict()}")
        
        result = WearableService.save_manual_entry(
            user_id=current_user_id,
            data=data.dict(exclude_none=True)
        )
        
        return {
            "success": True,
            "message": "Health data saved successfully!",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving manual entry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_entry(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the most recent wearable entry."""
    try:
        latest = WearableService.get_latest(current_user_id)
        
        if not latest:
            return {
                "hasData": False,
                "message": "No wearable data found"
            }
        
        return {
            "hasData": True,
            "data": latest,
            "sleepHours": latest.get("sleep_hours"),
            "heartRate": latest.get("avg_heart_rate"),
            "steps": latest.get("steps"),
            "stressLevel": latest.get("stress_level"),
            "caloriesBurned": latest.get("calories_burned"),
            "date": latest.get("date"),
            "source": latest.get("source")
        }
        
    except Exception as e:
        logger.error(f"Error fetching latest wearable: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    limit: int = 30,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get wearable history for a user."""
    try:
        history = WearableService.get_all_for_user(current_user_id, limit=limit)
        return {"data": history, "count": len(history)}
        
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_health(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Analyze wearable data for health risks and send notifications.
    
    Returns analysis results and creates in-app notification + SMS if needed.
    """
    try:
        logger.info(f"🔍 Analyzing health data for user {current_user_id}")
        
        # Perform analysis
        analysis = WearableService.analyze_health_risks(current_user_id)
        
        if not analysis["has_risks"]:
            return {
                "success": True,
                "message": "✅ No health risks detected! Keep up the good work!",
                "analysis": analysis
            }
        
        # Create in-app notification using AlertService
        supabase = get_supabase(use_service_role=True)
        
        risk_emoji = {
            "low": "ℹ️",
            "medium": "⚠️",
            "high": "🚨",
            "critical": "🆘"
        }
        
        notification_title = f"{risk_emoji.get(analysis['risk_level'], '📊')} Health Analysis Alert"
        notification_body = f"{len(analysis['risks'])} health concern(s) detected:\n\n" + "\n".join(analysis['risks'][:3])
        
        # Create notification using AlertService
        try:
            notification_type = "warning" if analysis['risk_level'] in ["high", "critical"] else "info"
            await AlertService.create_in_app_notification(
                supabase=supabase,
                user_id=current_user_id,
                title=notification_title,
                body=notification_body,
                notification_type=notification_type,
                action_url="/device"
            )
            logger.info(f"✅ Created in-app notification for user {current_user_id}")
            
        except Exception as notif_error:
            logger.error(f"Failed to create notification: {notif_error}")
        
        # Send SMS if critical
        if analysis['risk_level'] in ["high", "critical"]:
            try:
                # Get user profile with phone number
                profile = supabase.table("profiles").select("phone_number").eq("id", current_user_id).single().execute()
                
                if profile.data and profile.data.get("phone_number"):
                    phone = profile.data["phone_number"]
                    sms_message = f"Nirvami Health Alert: {analysis['risks'][0]}. Check the app for recommendations."
                    
                    await AlertService.send_sms_alert(
                        to_phone=phone,
                        message=sms_message
                    )
                    
                    logger.info(f"📱 Sent SMS alert to user {current_user_id}")
                    
            except Exception as sms_error:
                logger.error(f"Failed to send SMS: {sms_error}")
        
        return {
            "success": True,
            "message": f"Analysis complete. {len(analysis['risks'])} risk(s) detected.",
            "analysis": analysis,
            "notification_sent": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
