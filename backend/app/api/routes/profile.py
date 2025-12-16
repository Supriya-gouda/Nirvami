"""Profile management routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import UserProfile, UpdateProfileRequest, UserPreferences
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from typing import Dict
import pandas as pd
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=UserProfile)
async def get_current_user_profile(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get current user's profile."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("profiles").select("*").eq("id", current_user_id).execute()
        if not result.data or len(result.data) == 0:
            # Profile doesn't exist - create it from auth user
            logger.warning(f"Profile not found for user {current_user_id}, attempting to create")
            try:
                supabase_admin = get_supabase(use_service_role=True)
                auth_user = supabase_admin.auth.admin.get_user_by_id(current_user_id)
                
                if auth_user and auth_user.user:
                    profile_data = {
                        "id": current_user_id,
                        "email": auth_user.user.email,
                        "full_name": auth_user.user.user_metadata.get("full_name", ""),
                        "created_at": datetime.now().isoformat()
                    }
                    create_result = supabase_admin.table("profiles").insert(profile_data).execute()
                    if create_result.data:
                        logger.info(f"✅ Profile created for user {current_user_id}")
                        return create_result.data[0]
            except Exception as create_error:
                logger.error(f"Failed to create profile: {create_error}")
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserProfile)
async def get_profile(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get user profile."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's profile"
        )
    
    supabase = get_supabase()
    
    try:
        result = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )


@router.put("", response_model=UserProfile)
async def update_current_user_profile(
    update_data: UpdateProfileRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update current user's profile."""
    supabase = get_supabase()
    
    try:
        # Update profile
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.table("profiles").update(update_dict).eq(
            "id", current_user_id
        ).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserProfile)
async def update_profile(
    user_id: str,
    update_data: UpdateProfileRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user profile."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other user's profile"
        )
    
    supabase = get_supabase()
    
    try:
        # Prepare update data
        update_dict = update_data.model_dump(exclude_unset=True)
        if update_dict:
            result = supabase.table("profiles").update(update_dict).eq("id", user_id).execute()
            return result.data[0]
        else:
            # Return unchanged profile
            result = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
            return result.data
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.get("/preferences")
async def get_current_user_preferences(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get current user's preferences."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("user_preferences").select("*").eq("user_id", current_user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        # Return default if not found
        return {
            "user_id": current_user_id,
            "preferences": {
                "notifications_enabled": True,
                "email_notifications": True,
                "crisis_alerts": True,
                "wellness_reminders": True,
                "theme": "light"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}")
        return {
            "user_id": current_user_id,
            "preferences": {}
        }


@router.put("/preferences")
async def update_current_user_preferences(
    preferences: Dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update current user's preferences."""
    supabase = get_supabase()
    
    try:
        # Upsert preferences
        result = supabase.table("user_preferences").upsert({
            "user_id": current_user_id,
            "preferences": preferences
        }).execute()
        
        return result.data[0] if result.data else {"user_id": current_user_id, "preferences": preferences}
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.get("/{user_id}/preferences", response_model=UserPreferences)
async def get_preferences(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get user preferences."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    supabase = get_supabase()
    
    try:
        result = supabase.table("user_preferences").select("*").eq("user_id", user_id).single().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}")
        # Return default preferences if not found
        return UserPreferences()


@router.put("/{user_id}/preferences", response_model=UserPreferences)
async def update_preferences(
    user_id: str,
    preferences: UserPreferences,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user preferences."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    supabase = get_supabase()
    
    try:
        pref_dict = preferences.model_dump()
        result = supabase.table("user_preferences").upsert({
            "user_id": user_id,
            **pref_dict
        }).execute()
        return result.data[0]
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/{user_id}/export")
async def export_user_data(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Export all user data as JSON/CSV."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Fetch all user data
        export_data = {}
        
        # Profile
        profile = supabase.table("profiles").select("*").eq("id", user_id).execute()
        export_data["profile"] = profile.data[0] if profile.data else None
        
        # Messages
        messages = supabase.table("messages").select("*").eq("user_id", user_id).execute()
        export_data["messages"] = messages.data
        
        # Emotions
        emotions = supabase.table("emotion_logs").select("*").eq("user_id", user_id).execute()
        export_data["emotion_logs"] = emotions.data
        
        # Aura
        aura = supabase.table("aura_entries").select("*").eq("user_id", user_id).execute()
        export_data["aura_entries"] = aura.data
        
        # Wellness scores
        wellness = supabase.table("wellness_scores").select("*").eq("user_id", user_id).execute()
        export_data["wellness_scores"] = wellness.data
        
        # Meals
        meals = supabase.table("meals").select("*").eq("user_id", user_id).execute()
        export_data["meals"] = meals.data
        
        # Wearable data
        wearable = supabase.table("wearable_snapshots").select("*").eq("user_id", user_id).execute()
        export_data["wearable_data"] = wearable.data
        
        export_data["export_date"] = datetime.now().isoformat()
        export_data["export_format"] = "json"
        
        return export_data
        
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/{user_id}")
async def delete_account(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete user account and all associated data."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Delete profile (cascade will handle related data)
        supabase.table("profiles").delete().eq("id", user_id).execute()
        
        return {"message": "Account deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/streak/current")
async def get_current_streak(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get current login streak and visit history.
    Never crashes - returns default data on any error.
    """
    try:
        # Use service role for reliable operations
        supabase = get_supabase(use_service_role=True)
        
        # Get preferences
        result = supabase.table("user_preferences").select("*").eq("user_id", current_user_id).execute()
        
        # Default streak data for new users or errors
        default_streak = {
            "current_streak": 0,
            "longest_streak": 0,
            "last_visit_date": None,
            "visit_dates": []
        }
        
        if not result.data or len(result.data) == 0:
            # No preferences yet - return defaults (will be created on first visit)
            logger.info(f"ℹ️ No streak data for user {current_user_id}, returning defaults")
            return default_streak
        
        prefs = result.data[0]
        streak_data = prefs.get("preferences", {}).get("streak_data", default_streak)
        
        # Ensure all required fields exist
        streak_data.setdefault("current_streak", 0)
        streak_data.setdefault("longest_streak", 0)
        streak_data.setdefault("last_visit_date", None)
        streak_data.setdefault("visit_dates", [])
        
        return streak_data
        
    except Exception as e:
        # NEVER CRASH - return default data
        logger.error(f"❌ Error fetching streak data for {current_user_id}: {e}")
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_visit_date": None,
            "visit_dates": []
        }


@router.post("/streak/record-visit")
async def record_visit(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Record a visit and update streak.
    Safe to call multiple times per day - idempotent.
    NEVER crashes - returns success even on DB errors.
    """
    from datetime import date, datetime
    
    today_str = date.today().isoformat()
    
    try:
        # Use service role to bypass RLS for reliable operations
        supabase = get_supabase(use_service_role=True)
        
        # Get current preferences
        result = supabase.table("user_preferences").select("*").eq("user_id", current_user_id).execute()
        
        # Initialize default streak data
        default_streak = {
            "current_streak": 1,
            "longest_streak": 1,
            "last_visit_date": today_str,
            "visit_dates": [today_str]
        }
        
        if not result.data or len(result.data) == 0:
            # No row exists - try to create one
            try:
                prefs = {
                    "user_id": current_user_id,
                    "preferences": {
                        "streak_data": default_streak
                    }
                }
                insert_result = supabase.table("user_preferences").insert(prefs).execute()
                if insert_result.data:
                    logger.info(f"✅ Created new user preferences for {current_user_id}, streak=1")
                    return {
                        "ok": True,
                        "streak_updated": True,
                        "current_streak": 1
                    }
            except Exception as insert_err:
                # Row might have been created by another request (race condition)
                # Try to fetch it again
                logger.warning(f"⚠️ Insert failed (likely race condition): {insert_err}")
                retry_result = supabase.table("user_preferences").select("*").eq("user_id", current_user_id).execute()
                if retry_result.data and len(retry_result.data) > 0:
                    # Successfully fetched after race condition
                    result = retry_result
                else:
                    # Complete failure - return graceful fallback
                    logger.error(f"❌ Failed to create or fetch preferences for {current_user_id}")
                    return {
                        "ok": True,
                        "streak_updated": False,
                        "current_streak": 0
                    }
        
        # Row exists - process streak update
        prefs = result.data[0]
        streak_data = prefs.get("preferences", {}).get("streak_data", default_streak.copy())
        
        last_visit = streak_data.get("last_visit_date")
        
        # Check if already visited today - IDEMPOTENT
        if last_visit == today_str:
            logger.info(f"ℹ️ User {current_user_id} already visited today, returning existing streak")
            return {
                "ok": True,
                "streak_updated": False,
                "current_streak": streak_data.get("current_streak", 0)
            }
        
        # Calculate new streak
        if last_visit:
            try:
                last_date = datetime.fromisoformat(last_visit).date()
                today_date = date.today()
                days_diff = (today_date - last_date).days
                
                if days_diff == 1:
                    # Consecutive day - increment streak
                    streak_data["current_streak"] = streak_data.get("current_streak", 0) + 1
                else:
                    # Streak broken - reset to 1
                    streak_data["current_streak"] = 1
            except (ValueError, TypeError) as date_err:
                logger.warning(f"⚠️ Invalid last_visit_date: {last_visit}, resetting streak")
                streak_data["current_streak"] = 1
        else:
            # First visit ever
            streak_data["current_streak"] = 1
        
        # Update longest streak
        streak_data["longest_streak"] = max(
            streak_data.get("longest_streak", 0),
            streak_data["current_streak"]
        )
        streak_data["last_visit_date"] = today_str
        
        # Update visit dates (keep last 30 days to prevent bloat)
        visit_dates = streak_data.get("visit_dates", [])
        if today_str not in visit_dates:
            visit_dates.append(today_str)
        visit_dates = visit_dates[-30:]  # Keep only last 30 days
        streak_data["visit_dates"] = visit_dates
        
        # Update database
        updated_prefs = prefs.get("preferences", {})
        updated_prefs["streak_data"] = streak_data
        
        update_result = supabase.table("user_preferences").update({
            "preferences": updated_prefs
        }).eq("user_id", current_user_id).execute()
        
        if update_result.data:
            logger.info(f"✅ Updated streak for {current_user_id}: {streak_data['current_streak']} days")
            return {
                "ok": True,
                "streak_updated": True,
                "current_streak": streak_data["current_streak"]
            }
        else:
            logger.warning(f"⚠️ Update returned no data for {current_user_id}")
            return {
                "ok": True,
                "streak_updated": False,
                "current_streak": streak_data["current_streak"]
            }
        
    except Exception as e:
        # NEVER CRASH - log error and return graceful fallback
        logger.error(f"❌ Error recording visit for {current_user_id}: {e}")
        logger.exception(e)
        return {
            "ok": True,
            "streak_updated": False,
            "current_streak": 0
        }

