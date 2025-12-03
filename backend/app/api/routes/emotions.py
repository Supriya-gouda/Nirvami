"""Emotion detection routes."""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import EmotionDetectionResponse, EmotionLog, EmotionAggregate
from app.api.routes.aura import create_aura_entry_from_emotion
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


def ensure_user_profile(supabase, user_id: str, email: str = None):
    """Ensure user has a profile record. Create if doesn't exist."""
    try:
        # Check if profile exists
        result = supabase.table("profiles").select("id").eq("id", user_id).execute()
        
        if not result.data or len(result.data) == 0:
            # Get email from auth user if not provided
            if not email:
                try:
                    auth_user = supabase.auth.admin.get_user_by_id(user_id)
                    if auth_user and auth_user.user:
                        email = auth_user.user.email
                except Exception as e:
                    logger.warning(f"Could not get email for user {user_id}: {e}")
                    email = f"user_{user_id[:8]}@nirvami.app"
            
            # Create profile
            logger.info(f"Creating profile for user {user_id} with email {email}")
            profile_data = {
                "id": user_id,
                "email": email,
                "consent_data_collection": True,
                "consent_ai_processing": True,
                "consent_notifications": True
            }
            insert_result = supabase.table("profiles").insert(profile_data).execute()
            logger.info(f"✅ Profile created for user {user_id}")
            
            # Also create user_preferences entry
            try:
                pref_data = {
                    "user_id": user_id,
                    "notification_email": True,
                    "notification_sms": False,
                    "notification_push": True,
                    "crisis_alerts_enabled": True,
                    "data_retention_days": 365,
                    "preferences": {}
                }
                supabase.table("user_preferences").insert(pref_data).execute()
                logger.info(f"✅ User preferences created for user {user_id}")
            except Exception as pref_error:
                logger.warning(f"Failed to create user_preferences: {pref_error}")
    except Exception as e:
        logger.error(f"Error ensuring profile exists: {e}", exc_info=True)
        # Don't fail the request if profile creation fails
        pass


class LogEmotionRequest(BaseModel):
    emotion: Optional[str] = None  # Legacy field
    mood: Optional[str] = None  # New field for mood popup
    intensity: int
    energy: Optional[int] = None  # Optional energy field
    notes: Optional[str] = None
    detected_from: Optional[str] = None  # Legacy field
    source: Optional[str] = None  # New field for mood popup


@router.post("/log")
async def log_emotion(
    data: LogEmotionRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Log an emotion entry for the user.
    
    Supports both legacy format (emotion, detected_from) and new mood popup format (mood, source).
    """
    # Use service role to bypass RLS policies
    supabase = get_supabase(use_service_role=True)
    
    try:
        # CRITICAL: Ensure user profile exists before inserting emotion log
        ensure_user_profile(supabase, current_user_id)
        
        # Determine if this is new mood popup format or legacy format
        is_mood_popup = data.mood is not None or data.source is not None
        
        if is_mood_popup:
            # New mood popup format
            if not data.mood:
                return JSONResponse(
                    status_code=400,
                    content={"ok": False, "detail": "mood field is required"}
                )
            if not data.intensity or data.intensity < 1 or data.intensity > 10:
                return JSONResponse(
                    status_code=400,
                    content={"ok": False, "detail": "intensity must be between 1 and 10"}
                )
            
            # Validate mood value - updated to match all frontend moods
            valid_moods = [
                "happy", "calm", "sad", "anxious", "tired", "frustrated",
                "grateful", "neutral", "angry", "low-energy", "energized", "confused"
            ]
            if data.mood not in valid_moods:
                return JSONResponse(
                    status_code=400,
                    content={"ok": False, "detail": f"mood must be one of: {', '.join(valid_moods)}"}
                )
            
            emotion_type = data.mood
            source = "manual"  # DB constraint: must be 'text', 'voice', or 'manual'
            
            # Build all_scores with mood, intensity, optional energy/notes, and sub_source
            all_scores = {
                "mood": data.mood,
                "intensity": data.intensity,
                "sub_source": data.source or "mood_popup"  # Track whether from mood_popup or other manual source
            }
            if data.energy is not None:
                if data.energy < 1 or data.energy > 10:
                    return JSONResponse(
                        status_code=400,
                        content={"ok": False, "detail": "energy must be between 1 and 10"}
                    )
                all_scores["energy"] = data.energy
            if data.notes:
                all_scores["notes"] = data.notes
        else:
            # Legacy format (backward compatibility)
            if not data.emotion:
                return JSONResponse(
                    status_code=400,
                    content={"ok": False, "detail": "emotion field is required"}
                )
            emotion_type = data.emotion
            source = data.detected_from or "manual"
            all_scores = {data.emotion: data.intensity / 10.0}
        
        # Validate source against DB constraint
        valid_sources = ["text", "voice", "manual"]
        if source not in valid_sources:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "detail": f"source must be one of: {', '.join(valid_sources)}"}
            )
        
        # Create emotion log entry matching schema: emotion_type, confidence, all_scores, source
        emotion_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user_id,
            "emotion_type": emotion_type,
            "confidence": data.intensity / 10.0,  # Convert intensity (1-10) to 0-1 confidence
            "all_scores": all_scores,
            "source": source,
            "message_id": None,  # Always NULL for manual logs
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("emotion_logs").insert(emotion_data).execute()
        
        if result.data and len(result.data) > 0:
            emotion_log_id = result.data[0]["id"]
            logger.info(f"Emotion logged for user {current_user_id}: {emotion_type} (source: {source})")
            
            # CRITICAL: Create/update aura_entry IMMEDIATELY based on this emotion
            # This triggers the real-time aura color update in the UI
            try:
                aura_entry = await create_aura_entry_from_emotion(current_user_id, emotion_type, data.intensity / 10.0, supabase)
                logger.info(f"✅ Aura color updated to {aura_entry.get('color_code') if aura_entry else 'unknown'} for user {current_user_id}")
            except Exception as aura_err:
                logger.error(f"❌ Failed to create aura entry: {aura_err}")
                # Don't fail the emotion log if aura creation fails
            
            # Return new API contract format for mood popup, legacy format otherwise
            if is_mood_popup:
                return JSONResponse(
                    status_code=200,
                    content={
                        "ok": True,
                        "emotion_log_id": emotion_log_id
                    }
                )
            else:
                # Legacy response format
                response_data = result.data[0]
                return {
                    "id": response_data["id"],
                    "user_id": response_data["user_id"],
                    "emotion": response_data["emotion_type"],
                    "intensity": data.intensity,
                    "notes": data.notes,
                    "detected_from": response_data["source"],
                    "created_at": response_data["created_at"]
                }
        else:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "detail": "Failed to log emotion - no data returned"}
            )
            
    except Exception as e:
        logger.error(f"Error logging emotion: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"ok": False, "detail": f"Failed to log emotion: {str(e)}"}
        )


@router.get("/latest")
async def get_latest_emotion(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the most recent emotion log for user."""
    # Use service role to bypass RLS
    supabase = get_supabase(use_service_role=True)
    
    try:
        result = supabase.table("emotion_logs").select("*").eq(
            "user_id", current_user_id
        ).order("created_at", desc=True).limit(1).execute()
        
        if not result.data or len(result.data) == 0:
            return None
        
        log = result.data[0]
        
        # Transform to match frontend interface
        return {
            "id": log["id"],
            "user_id": log["user_id"],
            "emotion_type": log.get("emotion_type", "neutral"),
            "confidence": log.get("confidence", 0.5),
            "all_scores": log.get("all_scores", {}),
            "source": log.get("source", "manual"),
            "created_at": log["created_at"]
        }
    except Exception as e:
        logger.error(f"Error fetching latest emotion: {e}", exc_info=True)
        return None


@router.get("/today/logged")
async def check_mood_logged_today(
    current_user_id: str = Depends(get_current_user_id)
):
    """Check if user has logged mood today."""
    supabase = get_supabase(use_service_role=True)
    
    try:
        today = date.today().isoformat()
        
        # Check if there's any emotion log for today
        result = supabase.table("emotion_logs").select("id").eq(
            "user_id", current_user_id
        ).gte("created_at", today).lte(
            "created_at", f"{today}T23:59:59"
        ).limit(1).execute()
        
        logged_today = len(result.data) > 0 if result.data else False
        
        return {
            "logged_today": logged_today,
            "date": today
        }
    except Exception as e:
        logger.error(f"Error checking mood log: {e}", exc_info=True)
        # Return false on error so popup shows
        return {
            "logged_today": False,
            "date": date.today().isoformat()
        }


@router.get("/history")
async def get_emotion_logs(
    current_user_id: str = Depends(get_current_user_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: int = 7,
    limit: int = 100
):
    """Get emotion logs for user."""
    supabase = get_supabase(use_service_role=True)
    
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
        
        # Transform to match frontend EmotionLog interface
        transformed_data = []
        for log in result.data:
            transformed_data.append({
                "id": log["id"],
                "user_id": log["user_id"],
                "emotion": log.get("emotion_type", "neutral"),
                "intensity": int(log.get("confidence", 0.5) * 10),  # Convert confidence back to 1-10
                "notes": log.get("notes"),
                "detected_from": log.get("source", "manual"),
                "created_at": log["created_at"]
            })
        
        return transformed_data
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
    supabase = get_supabase(use_service_role=True)
    
    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = supabase.table("emotion_aggregates").select("*").eq(
            "user_id", current_user_id
        ).gte("date", since_date).order("date", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching aggregates: {e}")
        raise


@router.get("/today/logged")
async def check_mood_logged_today(
    current_user_id: str = Depends(get_current_user_id)
):
    """Check if user has logged a mood today via manual entry or mood popup."""
    supabase = get_supabase(use_service_role=True)
    today_date = date.today().isoformat()
    
    try:
        # Check for any manual mood logs today (source='manual' with sub_source in all_scores)
        result = supabase.table("emotion_logs").select("id").eq(
            "user_id", current_user_id
        ).eq("source", "manual").gte(
            "created_at", today_date
        ).limit(1).execute()
        
        has_logged = len(result.data) > 0 if result.data else False
        
        return {
            "logged_today": has_logged,
            "date": today_date
        }
    except Exception as e:
        logger.error(f"Error checking mood log: {e}")
        return {"logged_today": False, "date": today_date}
