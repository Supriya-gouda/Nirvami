"""Yoga and Sound Therapy content routes."""
from fastapi import APIRouter, Depends, Query
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/poses")
async def get_yoga_poses(
    dosha: Optional[str] = Query(None, description="Filter by dosha type (vata, pitta, kapha)"),
    emotion: Optional[str] = Query(None, description="Filter by emotion tag"),
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """
    Get yoga poses filtered by dosha and/or emotion.
    
    Returns poses that match the specified dosha and emotion tags.
    """
    try:
        query = supabase.table("yoga_poses").select("*")
        
        # Apply filters if provided
        conditions = []
        if dosha:
            # Filter where dosha_tags array contains the specified dosha
            query = query.contains("dosha_tags", [dosha.lower()])
        
        if emotion:
            # Filter where emotion_tags array contains the specified emotion
            query = query.contains("emotion_tags", [emotion.lower()])
        
        result = query.execute()
        
        logger.info(f"Retrieved {len(result.data)} yoga poses for user {current_user_id}")
        
        return {
            "success": True,
            "poses": result.data,
            "count": len(result.data),
            "filters": {
                "dosha": dosha,
                "emotion": emotion
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching yoga poses: {e}")
        return {
            "success": False,
            "poses": [],
            "count": 0,
            "error": str(e)
        }


@router.get("/sound-tracks")
async def get_sound_tracks(
    dosha: Optional[str] = Query(None, description="Filter by dosha type (vata, pitta, kapha)"),
    mood: Optional[str] = Query(None, description="Filter by mood/emotion"),
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """
    Get sound therapy tracks filtered by dosha and/or mood.
    
    Returns tracks that match the specified dosha and mood.
    """
    try:
        query = supabase.table("sound_tracks").select("*")
        
        # Apply filters if provided
        if dosha:
            # Filter where dosha_tags array contains the specified dosha
            query = query.contains("dosha_tags", [dosha.lower()])
        
        if mood:
            # Filter where emotion_tags array contains the specified mood/emotion
            query = query.contains("emotion_tags", [mood.lower()])
        
        result = query.execute()
        
        logger.info(f"Retrieved {len(result.data)} sound tracks for user {current_user_id}")
        
        return {
            "success": True,
            "tracks": result.data,
            "count": len(result.data),
            "filters": {
                "dosha": dosha,
                "mood": mood
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching sound tracks: {e}")
        return {
            "success": False,
            "tracks": [],
            "count": 0,
            "error": str(e)
        }


@router.post("/practice-log")
async def log_yoga_practice(
    pose_id: str,
    duration_minutes: int,
    notes: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Log a yoga practice session."""
    try:
        result = supabase.table("yoga_practice_logs").insert({
            "user_id": current_user_id,
            "pose_id": pose_id,
            "duration_minutes": duration_minutes,
            "notes": notes
        }).execute()
        
        logger.info(f"Logged yoga practice for user {current_user_id}")
        
        return {
            "success": True,
            "log": result.data[0] if result.data else None
        }
        
    except Exception as e:
        logger.error(f"Error logging yoga practice: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/sound-therapy-log")
async def log_sound_therapy(
    track_id: str,
    duration_minutes: int,
    notes: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Log a sound therapy listening session."""
    try:
        result = supabase.table("sound_therapy_logs").insert({
            "user_id": current_user_id,
            "track_id": track_id,
            "duration_minutes": duration_minutes,
            "notes": notes
        }).execute()
        
        logger.info(f"Logged sound therapy for user {current_user_id}")
        
        return {
            "success": True,
            "log": result.data[0] if result.data else None
        }
        
    except Exception as e:
        logger.error(f"Error logging sound therapy: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/ayurveda-resources")
async def get_ayurveda_resources(
    dosha: Optional[str] = Query(None, description="Filter by dosha type (vata, pitta, kapha)"),
    category: Optional[str] = Query(None, description="Filter by category (diet, yoga, meditation, lifestyle)"),
    limit: int = Query(10, description="Maximum number of resources to return"),
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """
    Get Ayurvedic wellness resources filtered by dosha and/or category.
    
    Returns educational content and tips personalized to user's dosha.
    """
    try:
        query = supabase.table("ayurveda_resources").select("*")
        
        # Apply filters if provided
        if dosha:
            # Filter where dosha_tags array contains the specified dosha
            query = query.contains("dosha_tags", [dosha.lower()])
        
        if category:
            # Filter by category
            query = query.eq("category", category.lower())
        
        # Limit results
        query = query.limit(limit)
        
        result = query.execute()
        
        logger.info(f"Retrieved {len(result.data)} ayurveda resources for user {current_user_id}")
        
        return {
            "success": True,
            "resources": result.data,
            "count": len(result.data),
            "filters": {
                "dosha": dosha,
                "category": category
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching ayurveda resources: {e}")
        return {
            "success": False,
            "resources": [],
            "count": 0,
            "error": str(e)
        }
