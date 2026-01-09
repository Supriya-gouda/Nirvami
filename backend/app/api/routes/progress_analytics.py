"""
Progress Analytics API Routes
Provides comprehensive analytics for the Progress & Analytics Page
"""
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException

from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import RecommendationCategory
from app.services.emotion_service import get_emotion_service

logger = logging.getLogger(__name__)

router = APIRouter()


def filter_sessions_by_date_timezone_aware(sessions: List[Dict], target_date: str) -> List[Dict]:
    """
    Filter practice sessions for a given date, accounting for timezone edge cases.
    
    For users in timezones ahead of UTC (like IST, UTC+5:30), practices completed
    late on the previous UTC day may actually be "today" in their local time.
    
    Example: 2026-01-06 23:58 UTC = 2026-01-07 05:28 IST
    
    Args:
        sessions: List of practice session records with 'completed_at' timestamps
        target_date: Target date string in YYYY-MM-DD format
        
    Returns:
        List of sessions that match the target date (with timezone tolerance)
    """
    from datetime import datetime, timedelta
    
    target_dt = datetime.fromisoformat(target_date)
    yesterday = (target_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    
    filtered_sessions = []
    for session in sessions:
        completed_at = session.get('completed_at', '')
        if completed_at and len(completed_at) >= 10:
            session_date = completed_at[:10]  # Extract YYYY-MM-DD
            
            # Include exact date matches
            if session_date == target_date:
                filtered_sessions.append(session)
            # Also include yesterday after 18:00 UTC (6 PM)
            # This handles timezones like IST (UTC+5:30) where 18:00 UTC = 23:30 IST (still same day locally)
            # and 23:00 UTC = 04:30 IST next day (shows as "today" for user)
            elif session_date == yesterday:
                time_part = completed_at[11:19]  # Extract HH:MM:SS
                if time_part >= "18:00:00":
                    filtered_sessions.append(session)
    
    return filtered_sessions


def calculate_mood_value(emotion_type: str, confidence: float) -> float:
    """Map emotions to numerical mood values using emotion type and confidence"""
    # Positive emotions: joy, happiness, calm, relaxed, love, gratitude, peaceful
    positive_emotions = ['joy', 'happiness', 'happy', 'joyful', 'calm', 'relaxed', 'love', 'gratitude', 'grateful', 'peaceful', 'content', 'excited']
    
    # Negative emotions: sadness, anger, anxiety, fear, stress, frustration
    negative_emotions = ['sadness', 'sad', 'anger', 'angry', 'anxiety', 'anxious', 'fear', 'fearful', 'stress', 'stressed', 'frustration', 'frustrated', 'overwhelmed']
    
    # Neutral emotions
    neutral_emotions = ['neutral', 'mixed', 'tired']
    
    emotion_lower = emotion_type.lower()
    
    if emotion_lower in positive_emotions:
        # Positive: confidence pushes score toward 10
        return 5.0 + (confidence * 5.0)  # Range: 5-10
    elif emotion_lower in negative_emotions:
        # Negative: confidence pushes score toward 1
        return 5.0 - (confidence * 4.0)  # Range: 1-5
    else:
        # Neutral: baseline around 5
        return 5.0


def calculate_stress_score(emotions_data: List[Dict]) -> float:
    """Calculate stress score from negative emotion confidence values"""
    if not emotions_data:
        return 0.0
    
    # Stress-related negative emotions
    stress_emotions = ['stress', 'stressed', 'fear', 'fearful', 'anxiety', 'anxious', 'anger', 'angry', 'frustration', 'frustrated', 'overwhelmed']
    stress_confidences = []
    
    for entry in emotions_data:
        emotion_type = entry.get('emotion_type', entry.get('emotion', '')).lower()
        confidence = entry.get('confidence', 0.5)
        
        if emotion_type in stress_emotions:
            # Normalize confidence (0-1) to 1-10 scale
            stress_confidences.append(confidence * 10)
    
    if not stress_confidences:
        return 0.0
    
    # Return average stress (1-10 scale)
    return sum(stress_confidences) / len(stress_confidences)


def calculate_consistency_score(completion_history: List[Dict]) -> float:
    """
    Calculate consistency score based on daily completion streak history
    - 7-day streak → 10/10
    - 3-day streak → ~4.2
    - Small gaps reduce slowly, long gaps reduce heavily
    - No history → 0
    """
    if not completion_history or len(completion_history) == 0:
        return 0.0  # No history = 0 score
    
    if len(completion_history) == 1:
        return 1.4  # Single day = minimal score
    
    # Sort by date
    sorted_history = sorted(completion_history, key=lambda x: x['date'])
    
    streak_lengths = []
    current_streak = 1
    gap_penalties = []
    
    for i in range(1, len(sorted_history)):
        prev_date = datetime.fromisoformat(sorted_history[i-1]['date']).date()
        curr_date = datetime.fromisoformat(sorted_history[i]['date']).date()
        
        day_diff = (curr_date - prev_date).days
        
        if day_diff == 1:
            # Consecutive days
            current_streak += 1
        elif day_diff <= 3:
            # Small break (1-3 days) - minor penalty
            gap_penalties.append(day_diff * 0.5)
            streak_lengths.append(current_streak)
            current_streak = 1
        else:
            # Long break (>3 days) - significant penalty
            gap_penalties.append(day_diff * 1.5)
            streak_lengths.append(current_streak)
            current_streak = 1
    
    streak_lengths.append(current_streak)
    
    # Calculate base score: 7-day streak = 10, scales proportionally
    max_streak = max(streak_lengths) if streak_lengths else 1
    base_score = min(10, (max_streak / 7) * 10)  # 7 days = 10 points
    
    # Apply gap penalties
    total_penalty = sum(gap_penalties)
    penalty_factor = min(total_penalty * 0.1, 5)  # Cap penalty at 5 points
    
    final_score = max(0, base_score - penalty_factor)
    return round(final_score, 1)


def calculate_wellness_score(avg_mood: float, stress_level: float, adherence: float, consistency: float) -> float:
    """
    Calculate comprehensive wellness score using specified model:
    - Emotion health (mood + stress) = 40%
    - Engagement (adherence) = 30%
    - Practice consistency = 30%
    """
    # Emotion score from mood and stress (40% weight)
    # Normalize stress (inverse - lower stress is better)
    normalized_stress = 10 - stress_level
    emotion_score = (avg_mood + normalized_stress) / 2  # Average of mood and inverted stress
    
    # Engagement score from adherence (30% weight)
    # Normalize adherence from percentage to 0-10 scale
    engagement_score = adherence / 10
    
    # Consistency score already on 0-10 scale (30% weight)
    
    # Calculate weighted wellness score
    wellness = (
        (emotion_score * 0.4) +
        (engagement_score * 0.3) +
        (consistency * 0.3)
    )
    
    return round(wellness, 1)


@router.get("/dashboard-metrics")
async def get_dashboard_metrics(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get all 7 dashboard metrics for today:
    1. Avg Mood (Today)
    2. Stress Level (Today)
    3. Total Recommendations Today
    4. Completed Recommendations Today
    5. Adherence Value (Today)
    6. Consistency Score
    7. Wellness Score
    """
    try:
        supabase = get_supabase(use_service_role=True)  # Use service role to bypass RLS
        today = date.today().isoformat()
        
        # 1 & 2: Avg Mood and Stress Level from emotion_logs
        emotion_result = supabase.table("emotion_logs")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("created_at", f"{today}T00:00:00")\
            .lte("created_at", f"{today}T23:59:59")\
            .execute()
        
        emotions_today = emotion_result.data or []
        
        if emotions_today:
            mood_values = [
                calculate_mood_value(
                    e.get('emotion_type', e.get('emotion', 'neutral')),
                    e.get('confidence', 0.5)
                ) for e in emotions_today
            ]
            avg_mood = round(sum(mood_values) / len(mood_values), 1)
            stress_level = round(calculate_stress_score(emotions_today), 1)
            logger.info(f"[Progress] Avg Mood computed: {avg_mood} from {len(emotions_today)} emotions")
            logger.info(f"[Progress] Stress Level computed: {stress_level}")
        else:
            avg_mood = None
            stress_level = None
            logger.info("[Progress] No mood data for today")
        
        # 3 & 4: Recommendations (total and completed)
        logger.info(f"[Progress] Fetching recommendations for user {current_user_id} on {today}")
        recs_result = supabase.table("recommendations")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .eq("date", today)\
            .execute()
        
        recommendations_today = recs_result.data or []
        total_recommendations = len(recommendations_today)
        logger.info(f"[Progress] Found {total_recommendations} recommendations")
        
        # Get completed recommendations by checking practice_sessions table
        # Fetch all recent sessions to handle timezone-aware filtering
        sessions_result = supabase.table("practice_sessions")\
            .select("recommendation_id, completed_at")\
            .eq("user_id", current_user_id)\
            .not_.is_("recommendation_id", "null")\
            .execute()
        
        # Filter sessions for today using timezone-aware logic
        today_sessions = filter_sessions_by_date_timezone_aware(sessions_result.data or [], today)
        
        completed_rec_ids = set(s['recommendation_id'] for s in today_sessions)
        completed_recommendations = len(completed_rec_ids)
        
        logger.info(f"[Progress] Total Recommendations Today: {total_recommendations}")
        logger.info(f"[Progress] Completed Recommendations Today: {completed_recommendations}")
        
        # 5: Adherence Value
        adherence = round((completed_recommendations / total_recommendations * 100), 1) if total_recommendations > 0 else None
        logger.info(f"[Progress] Adherence updated: {adherence}%" if adherence else "[Progress] No adherence data (no recommendations)")
        
        # 6: Consistency Score - based on completion history from practice_sessions
        # Get last 30 days of practice sessions to calculate consistency
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date().isoformat()
        sessions_history = supabase.table("practice_sessions")\
            .select("completed_at, recommendation_id")\
            .eq("user_id", current_user_id)\
            .gte("completed_at", f"{thirty_days_ago}T00:00:00")\
            .not_.is_("recommendation_id", "null")\
            .execute()
        
        # Group by date and count completions per day
        completion_by_date = {}
        for session in (sessions_history.data or []):
            completed_at = session.get('completed_at')
            if completed_at:
                # Extract date from timestamp
                session_date = completed_at.split('T')[0]
                if session_date not in completion_by_date:
                    completion_by_date[session_date] = {'completed': 0}
                completion_by_date[session_date]['completed'] += 1
        
        # Filter days with meaningful completion (at least 2 practices completed)
        meaningful_days = [
            {'date': d, 'completed': completion_by_date[d]['completed']}
            for d in completion_by_date
            if completion_by_date[d]['completed'] >= 2
        ]
        
        consistency_score = calculate_consistency_score(meaningful_days)
        logger.info(f"[Progress] Consistency score recalculated: {consistency_score} (based on {len(meaningful_days)} days with 2+ completions)")
        
        # 7: Wellness Score
        if avg_mood is not None and stress_level is not None and adherence is not None:
            wellness_score = calculate_wellness_score(avg_mood, stress_level, adherence, consistency_score)
            logger.info(f"[Progress] Wellness Score computed: {wellness_score}")
        else:
            wellness_score = None
            logger.info("[Progress] Wellness Score: insufficient data")
        
        return {
            "avg_mood_today": avg_mood,
            "stress_level_today": stress_level,
            "total_recommendations_today": total_recommendations,
            "completed_recommendations_today": completed_recommendations,
            "adherence_value_today": adherence,
            "consistency_score": consistency_score,
            "wellness_score": wellness_score,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emotion-trends")
async def get_emotion_trends(
    days: int = 7,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get emotion trends grouped by positive/negative/neutral percentages.
    
    Returns daily emotion distribution as percentages (summing to 100% per day).
    Uses confidence-weighted scoring for accurate representation.
    
    Automatically updates today's data and retrieves stored data for past dates.
    """
    try:
        supabase = get_supabase(use_service_role=True)
        emotion_service = get_emotion_service()
        
        today = date.today()
        start_date = today - timedelta(days=days - 1)  # Include today
        
        # Update today's emotion summary (always recompute for current day)
        logger.info(f"Updating emotion summary for today: {today}")
        
        # Fetch today's emotions
        today_emotions = supabase.table("emotion_logs")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("created_at", f"{today.isoformat()}T00:00:00")\
            .execute()
        
        # Compute and store today's summary
        if today_emotions.data:
            today_summary = emotion_service.compute_daily_emotion_summary(
                today_emotions.data,
                today
            )
            
            # Store/update today's summary
            emotion_service.store_daily_emotion_summary(
                supabase,
                current_user_id,
                today,
                today_summary
            )
        
        # Fetch stored summaries from database for the entire date range
        result = supabase.table("daily_emotion_summary")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("date", start_date.isoformat())\
            .lte("date", today.isoformat())\
            .order("date", desc=False)\
            .execute()
        
        stored_summaries = result.data or []
        
        # Create a map of existing summaries
        summary_map = {item['date']: item for item in stored_summaries}
        
        # Fill in missing dates with computed summaries (backfill for past dates)
        current_date = start_date
        all_trends = []
        
        while current_date <= today:
            date_str = current_date.isoformat()
            
            if date_str in summary_map:
                # Use stored summary
                summary = summary_map[date_str]
                all_trends.append({
                    'date': date_str,
                    'positive': summary['positive_percent'],
                    'negative': summary['negative_percent'],
                    'neutral': summary['neutral_percent']
                })
            else:
                # Compute and store summary for missing past date
                next_date_str = (current_date + timedelta(days=1)).isoformat()
                
                emotions = supabase.table("emotion_logs")\
                    .select("*")\
                    .eq("user_id", current_user_id)\
                    .gte("created_at", f"{date_str}T00:00:00")\
                    .lt("created_at", f"{next_date_str}T00:00:00")\
                    .execute()
                
                if emotions.data:
                    computed_summary = emotion_service.compute_daily_emotion_summary(
                        emotions.data,
                        current_date
                    )
                    
                    # Store the computed summary (only if past date)
                    emotion_service.store_daily_emotion_summary(
                        supabase,
                        current_user_id,
                        current_date,
                        computed_summary
                    )
                    
                    all_trends.append({
                        'date': date_str,
                        'positive': computed_summary['positive_percent'],
                        'negative': computed_summary['negative_percent'],
                        'neutral': computed_summary['neutral_percent']
                    })
                else:
                    # No emotions for this date - use neutral default
                    all_trends.append({
                        'date': date_str,
                        'positive': 0.0,
                        'negative': 0.0,
                        'neutral': 100.0
                    })
            
            current_date += timedelta(days=1)
        
        logger.info(f"Returning {len(all_trends)} days of emotion trends")
        
        return {"trends": all_trends}
        
    except Exception as e:
        logger.error(f"Error fetching emotion trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wellness-trend")
async def get_wellness_trend(
    days: int = 30,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get daily wellness scores over time
    """
    try:
        supabase = get_supabase(use_service_role=True)  # Use service role to bypass RLS
        start_date = (datetime.now() - timedelta(days=days)).date()
        end_date = datetime.now().date()
        
        # Fetch ALL data in bulk for the date range
        all_sessions_result = supabase.table("practice_sessions")\
            .select("recommendation_id, completed_at")\
            .eq("user_id", current_user_id)\
            .not_.is_("recommendation_id", "null")\
            .gte("completed_at", f"{start_date.isoformat()}T00:00:00")\
            .lte("completed_at", f"{end_date.isoformat()}T23:59:59")\
            .execute()
        all_sessions = all_sessions_result.data or []
        
        # Fetch all emotions in bulk
        all_emotions_result = supabase.table("emotion_logs")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("created_at", f"{start_date.isoformat()}T00:00:00")\
            .lte("created_at", f"{end_date.isoformat()}T23:59:59")\
            .execute()
        all_emotions = all_emotions_result.data or []
        
        # Fetch all recommendations in bulk
        all_recs_result = supabase.table("recommendations")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("date", start_date.isoformat())\
            .lte("date", end_date.isoformat())\
            .execute()
        all_recs = all_recs_result.data or []
        
        # Group data by date
        emotions_by_date = {}
        recs_by_date = {}
        
        for emotion in all_emotions:
            emotion_date = emotion['created_at'][:10]
            if emotion_date not in emotions_by_date:
                emotions_by_date[emotion_date] = []
            emotions_by_date[emotion_date].append(emotion)
        
        for rec in all_recs:
            rec_date = rec['date']
            if rec_date not in recs_by_date:
                recs_by_date[rec_date] = []
            recs_by_date[rec_date].append(rec)
        
        wellness_scores = []
        
        # Calculate wellness score for each day
        for i in range(days):
            target_date = start_date + timedelta(days=i)
            date_str = target_date.isoformat()
            
            emotions = emotions_by_date.get(date_str, [])
            recs = recs_by_date.get(date_str, [])
            total_recs = len(recs)
            
            # Filter sessions for this specific date using timezone-aware logic
            date_sessions = filter_sessions_by_date_timezone_aware(all_sessions, date_str)
            completed_rec_ids = set(s['recommendation_id'] for s in date_sessions)
            completed_recs = len(completed_rec_ids)
            
            # Calculate metrics for this day
            if emotions:
                mood_values = [
                    calculate_mood_value(
                        e.get('emotion_type', e.get('emotion', 'neutral')),
                        e.get('confidence', 0.5)
                    ) for e in emotions
                ]
                avg_mood = sum(mood_values) / len(mood_values)
                stress = calculate_stress_score(emotions)
            else:
                avg_mood = 5.0
                stress = 5.0
            
            adherence = (completed_recs / total_recs * 100) if total_recs > 0 else 0
            
            # Use simplified consistency for daily calculation
            consistency = 5.0
            
            wellness = calculate_wellness_score(avg_mood, stress, adherence, consistency)
            
            logger.info(f"[Wellness Trend] Date: {date_str}, Mood: {avg_mood:.1f}, Stress: {stress:.1f}, Adherence: {adherence:.1f}%, Consistency: {consistency:.1f}, Wellness: {wellness:.1f}")
            
            wellness_scores.append({
                'date': date_str,
                'wellness_score': wellness
            })
        
        return {"wellness_trend": wellness_scores}
        
    except Exception as e:
        logger.error(f"Error fetching wellness trend: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adherence-trend")
async def get_adherence_trend(
    days: int = 30,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get daily recommendation adherence over time
    """
    try:
        supabase = get_supabase(use_service_role=True)  # Use service role to bypass RLS
        start_date = (datetime.now() - timedelta(days=days)).date()
        end_date = datetime.now().date()
        
        # Fetch ALL data in bulk for the date range
        all_sessions_result = supabase.table("practice_sessions")\
            .select("recommendation_id, completed_at")\
            .eq("user_id", current_user_id)\
            .not_.is_("recommendation_id", "null")\
            .gte("completed_at", f"{start_date.isoformat()}T00:00:00")\
            .lte("completed_at", f"{end_date.isoformat()}T23:59:59")\
            .execute()
        all_sessions = all_sessions_result.data or []
        
        # Fetch all recommendations in bulk
        all_recs_result = supabase.table("recommendations")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .gte("date", start_date.isoformat())\
            .lte("date", end_date.isoformat())\
            .execute()
        all_recs = all_recs_result.data or []
        
        # Group recommendations by date
        recs_by_date = {}
        for rec in all_recs:
            rec_date = rec['date']
            if rec_date not in recs_by_date:
                recs_by_date[rec_date] = []
            recs_by_date[rec_date].append(rec)
        
        adherence_data = []
        
        for i in range(days):
            target_date = start_date + timedelta(days=i)
            date_str = target_date.isoformat()
            
            recs = recs_by_date.get(date_str, [])
            total = len(recs)
            
            # Filter sessions for this specific date using timezone-aware logic
            date_sessions = filter_sessions_by_date_timezone_aware(all_sessions, date_str)
            completed_rec_ids = set(s['recommendation_id'] for s in date_sessions)
            completed = len(completed_rec_ids)
            
            adherence = round((completed / total * 100), 1) if total > 0 else None
            
            adherence_data.append({
                'date': date_str,
                'total_recommendations': total,
                'completed_recommendations': completed,
                'adherence_percentage': adherence
            })
        
        return {"adherence_trend": adherence_data}
        
    except Exception as e:
        logger.error(f"Error fetching adherence trend: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
