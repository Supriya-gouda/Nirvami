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
