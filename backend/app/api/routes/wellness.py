"""Wellness scoring routes."""
from fastapi import APIRouter, Depends
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import WellnessScore
from typing import List, Dict
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def calculate_wellness_score(user_id: str, target_date: date, supabase) -> Dict:
    """Calculate real wellness score based on multiple factors."""
    
    # Initialize score components
    emotion_score = 50.0
    wearable_score = 50.0
    engagement_score = 50.0
    
    insights = []
    recommendations = []
    
    try:
        # 1. EMOTION SCORE (40% weight)
        emotion_result = supabase.table("emotion_aggregates").select("*").eq(
            "user_id", user_id
        ).eq("date", target_date.isoformat()).execute()
        
        if emotion_result.data and len(emotion_result.data) > 0:
            emotion_agg = emotion_result.data[0]
            emotion_dist = emotion_agg.get("emotion_distribution", {})
            
            # Calculate positive emotion percentage
            positive_emotions = ["joy", "happiness", "love", "excitement", "calm", "contentment"]
            negative_emotions = ["sadness", "anger", "fear", "anxiety", "disgust"]
            
            positive_score = sum(emotion_dist.get(e, 0) for e in positive_emotions)
            negative_score = sum(emotion_dist.get(e, 0) for e in negative_emotions)
            
            # Emotion score: 0-100 based on positive/negative ratio
            if positive_score + negative_score > 0:
                emotion_score = (positive_score / (positive_score + negative_score)) * 100
            else:
                emotion_score = 50.0
            
            # Add insights
            dominant = emotion_agg.get("dominant_emotion", "neutral")
            total_entries = emotion_agg.get("total_entries", 0)
            
            if dominant in positive_emotions:
                insights.append(f"Your dominant emotion today was {dominant} - great!")
            elif dominant in negative_emotions:
                insights.append(f"You experienced {dominant} today. Consider mindfulness exercises.")
                recommendations.append("Try 10 minutes of breathing exercises")
            
            if total_entries < 3:
                insights.append("Track your emotions more frequently for better insights")
        else:
            insights.append("No emotion data for today. Start logging your feelings!")
            recommendations.append("Log your current mood in the app")
        
        # 2. WEARABLE SCORE (30% weight)
        wearable_result = supabase.table("wearable_snapshots").select("*").eq(
            "user_id", user_id
        ).gte("timestamp", target_date.isoformat()).lte(
            "timestamp", (target_date + timedelta(days=1)).isoformat()
        ).order("timestamp", desc=True).limit(1).execute()
        
        if wearable_result.data and len(wearable_result.data) > 0:
            wearable = wearable_result.data[0]
            
            # Sleep score
            sleep_hours = wearable.get("sleep_hours", 0)
            if sleep_hours >= 7 and sleep_hours <= 9:
                sleep_score = 100
            elif sleep_hours >= 6 and sleep_hours <= 10:
                sleep_score = 75
            else:
                sleep_score = 50
            
            # HRV score
            hrv = wearable.get("hrv", 50)
            hrv_score = min(100, (hrv / 100) * 100)
            
            # Stress level (inverted)
            stress = wearable.get("stress_level", 50)
            stress_score = 100 - stress
            
            # Combined wearable score
            wearable_score = (sleep_score * 0.5 + hrv_score * 0.3 + stress_score * 0.2)
            
            # Add insights
            if sleep_hours < 6:
                insights.append(f"You only slept {sleep_hours} hours. Aim for 7-9 hours.")
                recommendations.append("Establish a consistent bedtime routine")
            
            if stress > 70:
                insights.append("Stress levels are high. Practice relaxation techniques.")
                recommendations.append("Try yoga or meditation for 15 minutes")
        else:
            insights.append("No wearable data available. Connect a fitness tracker.")
        
        # 3. ENGAGEMENT SCORE (30% weight)
        chat_result = supabase.table("messages").select("id", count="exact").eq(
            "user_id", user_id
        ).gte("created_at", target_date.isoformat()).lte(
            "created_at", (target_date + timedelta(days=1)).isoformat()
        ).execute()
        
        message_count = chat_result.count or 0
        
        if message_count >= 10:
            engagement_score = 100
            insights.append("Great engagement today!")
        elif message_count >= 5:
            engagement_score = 75
        elif message_count >= 1:
            engagement_score = 50
        else:
            engagement_score = 25
            recommendations.append("Chat with your wellness assistant for guidance")
        
        # Calculate overall weighted score
        overall_score = (
            emotion_score * 0.4 +
            wearable_score * 0.3 +
            engagement_score * 0.3
        )
        
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
                "engagement": round(engagement_score, 2)
            },
            "insights": insights,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error calculating wellness score: {e}")
        return {
            "user_id": user_id,
            "date": target_date.isoformat(),
            "overall_score": 50.0,
            "emotion_score": 50.0,
            "wearable_score": 50.0,
            "engagement_score": 50.0,
            "score_components": {"emotion": 50.0, "wearable": 50.0, "engagement": 50.0},
            "insights": ["Wellness data not available"],
            "recommendations": ["Continue using the app to track your wellness"]
        }


@router.get("/history", response_model=List[WellnessScore])
async def get_wellness_history(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 30
):
    """Get wellness score history."""
    supabase = get_supabase()
    
    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = supabase.table("wellness_scores").select("*").eq(
            "user_id", current_user_id
        ).gte("date", since_date).order("date", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching wellness history: {e}")
        raise
