"""Meal tracking routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import CreateMealRequest, Meal
from app.services.meal_service import MealCorrelationService
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
        meals_result = supabase.table("meals").select("*").eq(
            "user_id", current_user_id
        ).gte("meal_time", start_date.isoformat()).lte(
            "meal_time", end_date.isoformat()
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
            meal_time = datetime.fromisoformat(meal["meal_time"].replace("Z", "+00:00"))
            meal_name = meal.get("meal_text", "Unknown")
            
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


@router.post("/log", response_model=Meal)
async def create_meal(
    meal_data: CreateMealRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Log a meal."""
    supabase = get_supabase()
    
    try:
        # Prepare meal data
        new_meal = {
            "user_id": current_user_id,
            "meal_time": meal_data.meal_time.isoformat() if meal_data.meal_time else datetime.now().isoformat(),
            "meal_type": meal_data.meal_type,
            "meal_text": meal_data.meal_text,
            "ingredients": meal_data.ingredients,
            "calories": meal_data.calories,
            "dosha_impact_tags": meal_data.dosha_impact_tags
        }
        
        # Insert into database
        result = supabase.table("meals").insert(new_meal).execute()
        
        if not result.data:
            raise Exception("Failed to create meal record")
            
        logger.info(f"Created meal for user {current_user_id}: {meal_data.meal_text}")
        
        return result.data[0]
        
    except Exception as e:
        logger.error(f"Error creating meal: {e}")
        raise


@router.get("/history", response_model=List[Meal])
async def get_meals(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 7
):
    """Get meal history."""
    supabase = get_supabase()
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query database
        result = supabase.table("meals") \
            .select("*") \
            .eq("user_id", current_user_id) \
            .gte("meal_time", start_date.isoformat()) \
            .order("meal_time", desc=True) \
            .execute()
            
        logger.info(f"Retrieved {len(result.data)} meals for user {current_user_id}")
        
        return result.data
        
    except Exception as e:
        logger.error(f"Error fetching meals: {e}")
        raise


@router.get("/correlations")
async def get_meal_correlations(
    current_user_id: str = Depends(get_current_user_id),
    limit: int = 10
):
    """
    Get food insights showing which foods boost or drop mood.
    Returns top foods that correlate with positive/negative emotions.
    """
    try:
        insights = MealCorrelationService.get_food_insights(current_user_id, limit=limit)
        
        return {
            "mood_boosting_foods": insights["mood_boosting"][:3],  # Top 3
            "foods_to_watch": insights["mood_dropping"][:3],  # Top 3 worst
            "all_mood_boosting": insights["mood_boosting"],
            "all_mood_dropping": insights["mood_dropping"],
            "total_foods_analyzed": insights["total_analyzed"]
        }
        
    except Exception as e:
        logger.error(f"Error getting meal correlations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-correlations")
async def trigger_correlation_analysis(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Trigger meal-emotion correlation analysis for current user.
    This calculates and stores correlations in the database.
    """
    try:
        result = MealCorrelationService.run_correlation_analysis(current_user_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing correlations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
