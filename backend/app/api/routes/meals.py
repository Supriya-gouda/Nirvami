"""Meal tracking routes."""
from fastapi import APIRouter, Depends
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import CreateMealRequest, Meal
from typing import List
from datetime import date, datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/mood-correlations")
async def get_meal_mood_correlations(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 30
):
    """Get correlations between meals and mood."""
    try:
        supabase = get_supabase()
        
        # Get date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Fetch all meals in the period
        meals_result = supabase.table("meal_logs").select("*").eq(
            "user_id", current_user_id
        ).gte("timestamp", start_date.isoformat()).lte(
            "timestamp", end_date.isoformat()
        ).execute()
        
        if not meals_result.data or len(meals_result.data) == 0:
            return {"correlations": [], "period_days": days}
        
        # Fetch all emotion logs in the period
        emotions_result = supabase.table("emotion_logs").select("*").eq(
            "user_id", current_user_id
        ).gte("created_at", start_date.isoformat()).lte(
            "created_at", end_date.isoformat()
        ).execute()
        
        # Group meals by food name and calculate correlations
        meal_mood_map = defaultdict(list)
        
        for meal in meals_result.data:
            meal_time = datetime.fromisoformat(meal["timestamp"].replace("Z", "+00:00"))
            meal_name = meal.get("meal_name", "Unknown")
            
            # Find emotions 2-3 hours after meal
            post_meal_start = meal_time + timedelta(hours=2)
            post_meal_end = meal_time + timedelta(hours=3)
            
            # Calculate mood impact based on emotions after eating
            positive_emotions = ["joy", "happiness", "contentment", "calm", "love", "excitement"]
            negative_emotions = ["sadness", "anger", "anxiety", "fear", "disgust"]
            
            mood_scores = []
            
            for emotion in emotions_result.data:
                emotion_time = datetime.fromisoformat(emotion["created_at"].replace("Z", "+00:00"))
                
                if post_meal_start <= emotion_time <= post_meal_end:
                    emotion_type = emotion.get("emotion_type", "").lower()
                    confidence = emotion.get("confidence", 0.5)
                    
                    if emotion_type in positive_emotions:
                        mood_scores.append(confidence)
                    elif emotion_type in negative_emotions:
                        mood_scores.append(-confidence)
            
            if mood_scores:
                avg_mood = sum(mood_scores) / len(mood_scores)
                meal_mood_map[meal_name].append(avg_mood)
        
        # Calculate correlations
        correlations = []
        
        for food, moods in meal_mood_map.items():
            if len(moods) > 0:
                avg_impact = sum(moods) / len(moods)
                # Normalize to 0-1 scale (from -1 to 1)
                normalized_impact = (avg_impact + 1) / 2
                
                correlations.append({
                    "food": food,
                    "mood_impact": round(normalized_impact, 2),
                    "occurrences": len(moods),
                    "avg_mood_change": round(avg_impact, 2)
                })
        
        # Sort by mood impact (descending)
        correlations.sort(key=lambda x: x["mood_impact"], reverse=True)
        
        return {
            "correlations": correlations,
            "period_days": days,
            "total_meals": len(meals_result.data),
            "analyzed_foods": len(correlations)
        }
        
    except Exception as e:
        logger.error(f"Error getting meal correlations: {e}")
        return {"correlations": [], "period_days": days}


@router.post("/", response_model=Meal)
async def create_meal(
    meal_data: CreateMealRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Log a meal."""
    supabase = get_supabase()
    
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Error creating meal: {e}")
        raise


@router.get("/", response_model=List[Meal])
async def get_meals(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 7
):
    """Get meal history."""
    supabase = get_supabase()
    
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Error fetching meals: {e}")
        raise
