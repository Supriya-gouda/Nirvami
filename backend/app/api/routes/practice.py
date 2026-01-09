"""Practice session routes for tracking user practice completions."""
from fastapi import APIRouter, Depends, HTTPException, Body
from app.models.schemas import PracticeSession, PracticeContent, PracticeStreak
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


class CreatePracticeSessionRequest(BaseModel):
    practice_type: str
    practice_name: str
    duration_minutes: int
    recommendation_id: Optional[str] = None
    completion_status: str = "completed"
    notes: Optional[str] = None
    difficulty_rating: Optional[int] = None
    satisfaction_rating: Optional[int] = None


@router.get("/content/{practice_name}")
async def get_practice_content(
    practice_name: str,
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Get detailed practice content including YouTube video and animation steps."""
    try:
        # Get practice content from database
        result = supabase.table("practice_content").select("*").eq("practice_name", practice_name).execute()
        
        if not result.data or len(result.data) == 0:
            # Try to find in yoga_content table as fallback
            yoga_result = supabase.table("yoga_content").select("*").eq("name", practice_name).execute()
            
            if yoga_result.data and len(yoga_result.data) > 0:
                pose = yoga_result.data[0]
                # Convert yoga_content to practice_content format
                return {
                    "success": True,
                    "practice": {
                        "practice_type": "yoga",
                        "practice_name": pose["name"],
                        "sanskrit_name": pose.get("sanskrit_name"),
                        "description": pose.get("instructions"),
                        "benefits": pose.get("benefits", []),
                        "difficulty": pose.get("difficulty", "beginner"),
                        "duration_min": pose.get("duration_min", 1),
                        "duration_max": pose.get("duration_max", 5),
                        "youtube_video_id": None,  # Will be populated
                        "avatar_animation_steps": pose.get("instructions"),
                        "tts_instructions": [pose.get("instructions", "")],
                        "dosha_tags": pose.get("dosha_tags", []),
                        "emotion_tags": pose.get("emotion_tags", []),
                        "category": pose.get("category"),
                        "icon": pose.get("icon")
                    }
                }
            
            raise HTTPException(status_code=404, detail=f"Practice content not found: {practice_name}")
        
        return {
            "success": True,
            "practice": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching practice content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching practice content: {str(e)}")


@router.post("/sessions")
async def create_practice_session(
    request: CreatePracticeSessionRequest = Body(...),
    current_user_id: str = Depends(get_current_user_id)
):
    """Log a completed practice session."""
    try:
        # Use service role to bypass RLS for practice session creation
        from app.utils.database import get_supabase
        supabase = get_supabase(use_service_role=True)
        
        logger.info(f"📝 Creating practice session for user {current_user_id}: {request.practice_type} - {request.practice_name}")
        
        # Prepare session data with proper None handling
        session_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user_id,
            "practice_type": request.practice_type,
            "practice_name": request.practice_name,
            "duration_minutes": request.duration_minutes,
            "completed_at": datetime.utcnow().isoformat(),
            "completion_status": request.completion_status,
        }
        
        # Only add optional fields if they have values
        if request.recommendation_id:
            session_data["recommendation_id"] = request.recommendation_id
        if request.notes:
            session_data["notes"] = request.notes
        if request.difficulty_rating:
            session_data["difficulty_rating"] = request.difficulty_rating
        if request.satisfaction_rating:
            session_data["satisfaction_rating"] = request.satisfaction_rating
        
        result = supabase.table("practice_sessions").insert(session_data).execute()
        
        if not result.data:
            logger.error(f"❌ Failed to insert practice session to database")
            raise HTTPException(status_code=500, detail="Failed to create practice session")
        
        logger.info(f"✅ Practice Stored: {session_data['id']}")
        
        # Mark recommendation as completed if recommendation_id provided
        if request.recommendation_id:
            try:
                # First, get the current recommendation to preserve existing meta
                rec_result = supabase.table("recommendations").select("meta").eq("id", request.recommendation_id).execute()
                
                current_meta = {}
                if rec_result.data and len(rec_result.data) > 0:
                    current_meta = rec_result.data[0].get("meta", {}) or {}
                
                # Merge with new completion data
                updated_meta = {
                    **current_meta,
                    "completed": True,
                    "completed_at": datetime.utcnow().isoformat(),
                    "practice_session_id": session_data["id"]
                }
                
                # Update recommendation with merged meta AND mark Completed column as YES
                update_result = supabase.table("recommendations").update({
                    "meta": updated_meta,
                    "Completed": "YES"
                }).eq("id", request.recommendation_id).execute()
                
                if update_result.data:
                    logger.info(f"✅ Marked recommendation {request.recommendation_id} as completed (Completed=YES)")
                else:
                    logger.warning(f"⚠️ Could not mark recommendation {request.recommendation_id} as completed")
            except Exception as rec_error:
                logger.warning(f"⚠️ Failed to mark recommendation as completed: {rec_error}")
                # Non-critical, don't fail the request
        
        logger.info(f"✅ Created practice session for user {current_user_id}: {request.practice_name}")
        
        return {
            "success": True,
            "session": result.data[0],
            "message": f"Practice session '{request.practice_name}' logged successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating practice session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating practice session: {str(e)}")


@router.get("/sessions")
async def get_practice_sessions(
    limit: int = 30,
    practice_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Get user's practice session history."""
    try:
        query = supabase.table("practice_sessions").select("*").eq("user_id", current_user_id)
        
        if practice_type:
            query = query.eq("practice_type", practice_type)
        
        if start_date:
            query = query.gte("completed_at", start_date)
        
        if end_date:
            query = query.lte("completed_at", end_date)
        
        result = query.order("completed_at", desc=True).limit(limit).execute()
        
        return {
            "success": True,
            "sessions": result.data or [],
            "count": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching practice sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching practice sessions: {str(e)}")


@router.get("/streak")
async def get_practice_streak(
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Get user's practice streak information."""
    try:
        result = supabase.table("practice_streaks").select("*").eq("user_id", current_user_id).execute()
        
        if not result.data or len(result.data) == 0:
            # Initialize streak for new user
            return {
                "success": True,
                "streak": {
                    "current_streak": 0,
                    "longest_streak": 0,
                    "total_sessions": 0,
                    "last_practice_date": None
                }
            }
        
        return {
            "success": True,
            "streak": result.data[0]
        }
        
    except Exception as e:
        logger.error(f"Error fetching practice streak: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching practice streak: {str(e)}")


@router.get("/stats")
async def get_practice_stats(
    days: int = 30,
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Get practice statistics for the user."""
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get all sessions in date range
        result = supabase.table("practice_sessions")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("completed_at", start_date)\
            .execute()
        
        sessions = result.data or []
        
        # Calculate statistics
        total_sessions = len(sessions)
        total_minutes = sum(s.get("duration_minutes", 0) for s in sessions)
        
        # Count by practice type
        type_counts = {}
        for session in sessions:
            practice_type = session.get("practice_type", "other")
            type_counts[practice_type] = type_counts.get(practice_type, 0) + 1
        
        # Most practiced
        practice_counts = {}
        for session in sessions:
            practice_name = session.get("practice_name")
            practice_counts[practice_name] = practice_counts.get(practice_name, 0) + 1
        
        most_practiced = sorted(practice_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Average ratings
        ratings = [s.get("satisfaction_rating") for s in sessions if s.get("satisfaction_rating")]
        avg_satisfaction = sum(ratings) / len(ratings) if ratings else None
        
        return {
            "success": True,
            "stats": {
                "total_sessions": total_sessions,
                "total_minutes": total_minutes,
                "average_minutes_per_session": total_minutes / total_sessions if total_sessions > 0 else 0,
                "sessions_by_type": type_counts,
                "most_practiced": [{"practice": name, "count": count} for name, count in most_practiced],
                "average_satisfaction": avg_satisfaction,
                "days_analyzed": days
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating practice stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating practice stats: {str(e)}")


@router.get("/wellness-contribution")
async def get_wellness_contribution(
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Calculate how much practice sessions contribute to wellness score."""
    try:
        # Get today's sessions
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        result = supabase.table("practice_sessions")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("completed_at", today_start)\
            .execute()
        
        sessions = result.data or []
        
        # Calculate wellness contribution
        # Base: 2 points per session, max 10 points per day
        session_points = min(len(sessions) * 2, 10)
        
        # Bonus for duration (1 point per 10 minutes, max 5 points)
        total_minutes = sum(s.get("duration_minutes", 0) for s in sessions)
        duration_points = min(total_minutes // 10, 5)
        
        # Bonus for variety (1 point per unique practice type, max 5 points)
        unique_types = len(set(s.get("practice_type") for s in sessions))
        variety_points = min(unique_types, 5)
        
        total_contribution = session_points + duration_points + variety_points
        
        return {
            "success": True,
            "contribution": {
                "total_points": total_contribution,
                "session_points": session_points,
                "duration_points": duration_points,
                "variety_points": variety_points,
                "sessions_today": len(sessions),
                "total_minutes_today": total_minutes,
                "explanation": f"Your {len(sessions)} practice session(s) today contribute {total_contribution} points to your wellness score!"
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating wellness contribution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating wellness contribution: {str(e)}")


@router.get("/completion-summary")
async def get_completion_summary(
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Get user's completion summary based on practice sessions."""
    try:
        # Get all completed practice sessions
        result = supabase.table("practice_sessions")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .eq("completion_status", "completed")\
            .order("completed_at", desc=True)\
            .execute()
        
        sessions = result.data or []
        
        if not sessions:
            return {
                "success": True,
                "summary": {
                    "daily_completed_count": 0,
                    "last_completion_date": None,
                    "current_streak": 0,
                    "longest_streak": 0,
                    "lifetime_total_completed": 0
                }
            }
        
        # Calculate statistics from practice sessions
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        
        # Count today's completions
        today_count = sum(1 for s in sessions if datetime.fromisoformat(s['completed_at'].replace('Z', '+00:00')).date() == today)
        
        # Get last completion date
        last_completion = datetime.fromisoformat(sessions[0]['completed_at'].replace('Z', '+00:00')).date()
        
        # Calculate streak (simplified)
        current_streak = 1 if last_completion >= today - timedelta(days=1) else 0
        
        return {
            "success": True,
            "summary": {
                "daily_completed_count": today_count,
                "last_completion_date": last_completion.isoformat(),
                "current_streak": current_streak,
                "longest_streak": current_streak,
                "lifetime_total_completed": len(sessions)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching completion summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching completion summary: {str(e)}")
