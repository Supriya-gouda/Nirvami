import logging
from fastapi import APIRouter, Depends
from datetime import date, timedelta
from typing import List, Dict

from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import WellnessScore

logger = logging.getLogger(__name__)

router = APIRouter()

def calculate_wellness_score(user_id: str, target_date: date, supabase) -> Dict:
    """Calculate real wellness score based on multiple factors.

    Incorporates emotion aggregates, wearable snapshots (or fallback watch_data), and engagement data.
    """
    # Initialize score components
    emotion_score = 50.0
    wearable_score = 50.0
    engagement_score = 50.0
    insights: list[str] = []
    recommendations: list[str] = []
    try:
        # 1. EMOTION SCORE (40% weight)
        emotion_result = (
            supabase.table("emotion_aggregates")
            .select("*")
            .eq("user_id", user_id)
            .eq("date", target_date.isoformat())
            .execute()
        )
        if emotion_result.data and len(emotion_result.data) > 0:
            emotion_agg = emotion_result.data[0]
            emotion_dist = emotion_agg.get("emotion_distribution", {})
            positive_emotions = ["joy", "happiness", "love", "excitement", "calm", "contentment"]
            negative_emotions = ["sadness", "anger", "fear", "anxiety", "disgust"]
            positive_sum = sum(emotion_dist.get(e, 0) for e in positive_emotions)
            negative_sum = sum(emotion_dist.get(e, 0) for e in negative_emotions)
            if positive_sum + negative_sum > 0:
                emotion_score = (positive_sum / (positive_sum + negative_sum)) * 100
            else:
                emotion_score = 50.0
            dominant = emotion_agg.get("dominant_emotion", "neutral")
            total_entries = emotion_agg.get("total_entries", 0)
            if total_entries > 0:
                if dominant in positive_emotions:
                    insights.append(f"Your dominant emotion today was {dominant} - great!")
                elif dominant in negative_emotions:
                    insights.append(f"You experienced {dominant} today. Consider mindfulness exercises.")
                    recommendations.append("Try 10 minutes of breathing exercises")
                else:
                    insights.append("Your emotions were balanced today.")
            else:
                insights.append("No emotion entries recorded today.")
                recommendations.append("Log your emotions to track your mood.")
        # 2. WEARABLE SCORE (30% weight)
        wearable_result = (
            supabase.table("wearable_snapshots")
            .select("*")
            .eq("user_id", user_id)
            .gte("recorded_at", target_date.isoformat())
            .lte("recorded_at", (target_date + timedelta(days=1)).isoformat())
            .order("recorded_at", desc=True)
            .limit(1)
            .execute()
        )
        # Fallback to daily stats if no snapshots
        if not (wearable_result.data and len(wearable_result.data) > 0):
            wearable_result = (
                supabase.table("wearable_daily_stats")
                .select("*")
                .eq("user_id", user_id)
                .eq("date", target_date.isoformat())
                .execute()
            )
        if wearable_result.data and len(wearable_result.data) > 0:
            wearable = wearable_result.data[0]
            sleep_hours = wearable.get("sleep_hours", 0)
            steps = wearable.get("steps", 0)
            hrv = wearable.get("hrv", 0)
            stress = wearable.get("stress_level", 0)
            sleep_score = max(0, min(100, (sleep_hours / 8.0) * 100))
            activity_score = max(0, min(100, (steps / 10000.0) * 100))
            hrv_score = max(0, min(100, (hrv / 100.0) * 100))
            stress_score = 100 - stress if isinstance(stress, (int, float)) else 50
            wearable_score = (sleep_score * 0.4) + (activity_score * 0.3) + (hrv_score * 0.2) + (stress_score * 0.1)
            if sleep_hours < 6:
                insights.append(f"You only slept {sleep_hours:.1f} hours. Aim for 7‑9 hours.")
                recommendations.append("Establish a consistent bedtime routine")
            if steps < 5000:
                insights.append(f"You took only {steps} steps today. Increase activity.")
                recommendations.append("Take a 30‑minute walk.")
            if hrv < 40:
                insights.append("Low HRV detected. Consider relaxation techniques.")
                recommendations.append("Practice deep breathing exercises.")
        else:
            insights.append("No wearable data available for today.")
        # 3. ENGAGEMENT SCORE (30% weight)
        journal_result = (
            supabase.table("journal_entries")
            .select("id")
            .eq("user_id", user_id)
            .eq("date", target_date.isoformat())
            .execute()
        )
        goal_result = (
            supabase.table("goals")
            .select("id", "is_completed")
            .eq("user_id", user_id)
            .eq("target_date", target_date.isoformat())
            .execute()
        )
        # Get practice sessions for today
        practice_result = (
            supabase.table("practice_sessions")
            .select("id", "duration_minutes", "practice_type")
            .eq("user_id", user_id)
            .gte("completed_at", target_date.isoformat())
            .lte("completed_at", (target_date + timedelta(days=1)).isoformat())
            .execute()
        )
        
        journal_entries_count = len(journal_result.data) if journal_result.data else 0
        completed_goals_count = sum(1 for g in (goal_result.data or []) if g.get("is_completed"))
        total_goals_count = len(goal_result.data) if goal_result.data else 0
        practice_sessions = practice_result.data or []
        practice_count = len(practice_sessions)
        
        journal_score = min(100, (journal_entries_count / 1.0) * 50)
        if journal_entries_count == 0:
            insights.append("No journal entries today.")
            recommendations.append("Write a journal entry to reflect on your day.")
        elif journal_entries_count == 1:
            insights.append("You made one journal entry today.")
        else:
            insights.append(f"You made {journal_entries_count} journal entries today - great for reflection!")
        
        goal_score = 0
        if total_goals_count > 0:
            goal_score = (completed_goals_count / total_goals_count) * 100
            if completed_goals_count == total_goals_count:
                insights.append("All your goals for today were completed!")
            elif completed_goals_count > 0:
                insights.append(f"You completed {completed_goals_count} out of {total_goals_count} goals.")
            else:
                insights.append("No goals completed today.")
                recommendations.append("Review your goals and make them achievable.")
        else:
            insights.append("No goals set for today.")
            recommendations.append("Set daily goals to boost productivity.")
        
        # Calculate practice score
        practice_score = 0
        if practice_count > 0:
            # Base points: 2 per session
            base_points = min(practice_count * 2, 10)  # Max 10 pts from sessions
            
            # Duration bonus: 1 point per 10 minutes, max 5 pts
            total_duration = sum(p.get("duration_minutes", 0) for p in practice_sessions)
            duration_bonus = min(total_duration / 10, 5)
            
            # Variety bonus: 1 point per unique practice type, max 5 pts
            unique_types = len(set(p.get("practice_type", "") for p in practice_sessions))
            variety_bonus = min(unique_types, 5)
            
            practice_score = min(base_points + duration_bonus + variety_bonus, 100)
            
            insights.append(f"You completed {practice_count} practice session(s) today!")
            if total_duration >= 30:
                insights.append(f"Great job practicing for {total_duration} minutes!")
        else:
            insights.append("No practice sessions today.")
            recommendations.append("Try a guided yoga or meditation practice.")
        
        engagement_score = (journal_score * 0.3) + (goal_score * 0.3) + (practice_score * 0.4)
        overall_score = (emotion_score * 0.4) + (wearable_score * 0.3) + (engagement_score * 0.3)
        return {
            "user_id": user_id,
            "date": target_date.isoformat(),
            "overall_score": round(overall_score, 2),
            "emotion_score": round(emotion_score, 2),
            "wearable_score": round(wearable_score, 2),
            "engagement_score": round(engagement_score, 2),
            "score_components": {
                "emotion": round(emotion_score, 2),
                "wearable": round(wearable_score, 2),
                "engagement": round(engagement_score, 2),
            },
            "insights": list(set(insights)),
            "recommendations": list(set(recommendations)),
        }
    except Exception as e:
        logger.error(f"Error calculating wellness score for user {user_id} on {target_date}: {e}")
        return {
            "user_id": user_id,
            "date": target_date.isoformat(),
            "overall_score": 50.0,
            "emotion_score": 50.0,
            "wearable_score": 50.0,
            "engagement_score": 50.0,
            "score_components": {"emotion": 50.0, "wearable": 50.0, "engagement": 50.0},
            "insights": ["Wellness data not available due to an error."],
            "recommendations": ["Please try again later or contact support if the issue persists."],
        }

@router.get("/today")
async def get_today_wellness(
    current_user_id: str = Depends(get_current_user_id),
):
    """Get today's wellness score. Calculates and saves if not exists."""
    supabase = get_supabase()
    today = date.today()
    
    # Try to get existing score
    try:
        result = (
            supabase.table("wellness_scores")
            .select("*")
            .eq("user_id", current_user_id)
            .eq("date", today.isoformat())
            .execute()
        )
        
        if result.data and len(result.data) > 0:
            return result.data[0]
            
        # Calculate new score if not exists
        wellness_data = calculate_wellness_score(current_user_id, today, supabase)
        
        # Save to database
        try:
            # Use upsert with onConflict to handle existing records
            insert_result = supabase.table("wellness_scores").upsert(
                wellness_data,
                on_conflict="user_id,date"
            ).execute()
            if insert_result.data and len(insert_result.data) > 0:
                logger.info(f"Wellness score saved for user {current_user_id}: {wellness_data['overall_score']}")
                return insert_result.data[0]
            else:
                logger.warning(f"Wellness score calculated but not saved for user {current_user_id}")
                return wellness_data
        except Exception as save_error:
            logger.error(f"Error saving wellness score: {save_error}")
            # Return calculated data even if save fails
            return wellness_data
            
    except Exception as e:
        logger.error(f"Error fetching today's wellness: {e}")
        # Calculate and return default on error
        wellness_data = calculate_wellness_score(current_user_id, today, supabase)
        try:
            supabase.table("wellness_scores").upsert(
                wellness_data,
                on_conflict="user_id,date"
            ).execute()
        except:
            pass
        return wellness_data


@router.post("/compute")
async def compute_wellness(
    current_user_id: str = Depends(get_current_user_id),
    target_date: str = None,
):
    """Force recalculation of wellness score for a specific date."""
    supabase = get_supabase()
    
    # Use today if no date specified
    if target_date:
        try:
            calc_date = date.fromisoformat(target_date)
        except ValueError:
            calc_date = date.today()
    else:
        calc_date = date.today()
    
    try:
        # Calculate wellness score
        wellness_data = calculate_wellness_score(current_user_id, calc_date, supabase)
        
        # Save to database with upsert
        result = supabase.table("wellness_scores").upsert(
            wellness_data,
            on_conflict="user_id,date"
        ).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"Wellness score computed and saved for user {current_user_id} on {calc_date}: {wellness_data['overall_score']}")
            return result.data[0]
        else:
            logger.warning(f"Wellness score calculated but not saved properly")
            return wellness_data
            
    except Exception as e:
        logger.error(f"Error computing wellness score: {e}")
        raise


@router.get("/history", response_model=List[WellnessScore])
async def get_wellness_history(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 30,
):
    """Get wellness score history."""
    supabase = get_supabase()
    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()
        result = (
            supabase.table("wellness_scores")
            .select("*")
            .eq("user_id", current_user_id)
            .gte("date", since_date)
            .order("date", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Error fetching wellness history: {e}")
        raise


@router.get("/today-wearable-summary")
async def get_today_wearable_summary(
    target_date: str = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get comprehensive wearable summary with emotion inference and recommendations.
    
    Returns:
    {
        "date": "2025-11-23",
        "sleep_hours": 6.2,
        "avg_heart_rate": 88,
        "total_steps": 4200,
        "inferred_emotion": "stressed",
        "food_recommendations": [...],
        "yoga_recommendations": [...],
        "insights": [...]
    }
    """
    from app.services.wearable_service import WearableService
    
    try:
        if target_date:
            date_obj = date.fromisoformat(target_date)
        else:
            date_obj = date.today()
        
        summary = WearableService.get_today_summary(
            user_id=current_user_id,
            target_date=date_obj
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting wearable summary: {e}")
        raise
