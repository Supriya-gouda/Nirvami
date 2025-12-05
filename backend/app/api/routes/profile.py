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
    """Get current login streak and visit history."""
    supabase = get_supabase()
    
    try:
        # Get or create preferences
        result = supabase.table("user_preferences").select("*").eq("user_id", current_user_id).execute()
        
        if not result.data or len(result.data) == 0:
            # Create default preferences
            default_prefs = {
                "user_id": current_user_id,
                "preferences": {
                    "streak_data": {
                        "current_streak": 0,
                        "longest_streak": 0,
                        "last_visit_date": None,
                        "visit_dates": []
                    }
                }
            }
            create_result = supabase_admin = get_supabase(use_service_role=True)
            create_result = supabase_admin.table("user_preferences").insert(default_prefs).execute()
            prefs = create_result.data[0] if create_result.data else default_prefs
        else:
            prefs = result.data[0]
        
        streak_data = prefs.get("preferences", {}).get("streak_data", {
            "current_streak": 0,
            "longest_streak": 0,
            "last_visit_date": None,
            "visit_dates": []
        })
        
        return streak_data
        
    except Exception as e:
        logger.error(f"Error fetching streak data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch streak data")


@router.post("/streak/record-visit")
async def record_visit(
    current_user_id: str = Depends(get_current_user_id)
):
    """Record a visit and update streak."""
    from datetime import date
    
    supabase = get_supabase()
    today_str = date.today().isoformat()
    
    try:
        # Get current preferences
        result = supabase.table("user_preferences").select("*").eq("user_id", current_user_id).execute()
        
        if not result.data or len(result.data) == 0:
            # Create new preferences with first visit
            prefs = {
                "user_id": current_user_id,
                "preferences": {
                    "streak_data": {
                        "current_streak": 1,
                        "longest_streak": 1,
                        "last_visit_date": today_str,
                        "visit_dates": [today_str]
                    }
                }
            }
            supabase_admin = get_supabase(use_service_role=True)
            supabase_admin.table("user_preferences").insert(prefs).execute()
            return prefs["preferences"]["streak_data"]
        
        prefs = result.data[0]
        streak_data = prefs.get("preferences", {}).get("streak_data", {
            "current_streak": 0,
            "longest_streak": 0,
            "last_visit_date": None,
            "visit_dates": []
        })
        
        last_visit = streak_data.get("last_visit_date")
        visit_dates = streak_data.get("visit_dates", [])
        
        # Check if already visited today
        if last_visit == today_str:
            return streak_data
        
        # Add today to visit dates
        if today_str not in visit_dates:
            visit_dates.append(today_str)
        
        # Calculate streak
        from datetime import datetime, timedelta
        if last_visit:
            last_date = datetime.fromisoformat(last_visit).date()
            today_date = date.today()
            days_diff = (today_date - last_date).days
            
            if days_diff == 1:
                # Consecutive day
                streak_data["current_streak"] = streak_data.get("current_streak", 0) + 1
            else:
                # Streak broken
                streak_data["current_streak"] = 1
        else:
            # First visit
            streak_data["current_streak"] = 1
        
        # Update longest streak
        streak_data["longest_streak"] = max(
            streak_data.get("longest_streak", 0),
            streak_data["current_streak"]
        )
        streak_data["last_visit_date"] = today_str
        streak_data["visit_dates"] = visit_dates
        
        # Update preferences
        updated_prefs = prefs.copy()
        if "preferences" not in updated_prefs:
            updated_prefs["preferences"] = {}
        updated_prefs["preferences"]["streak_data"] = streak_data
        
        supabase.table("user_preferences").update({"preferences": updated_prefs["preferences"]}).eq(
            "user_id", current_user_id
        ).execute()
        
        return streak_data
        
    except Exception as e:
        logger.error(f"Error recording visit: {e}")
        raise HTTPException(status_code=500, detail="Failed to record visit")

