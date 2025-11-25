"""Meal correlation service for analyzing meal-emotion relationships."""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)


class MealCorrelationService:
    """Service for calculating and managing meal-emotion correlations."""
    
    @staticmethod
    def calculate_meal_emotion_correlations(user_id: str, days: int = 30) -> List[Dict]:
        """
        Calculate correlations between meals and emotions for a user.
        
        Args:
            user_id: User ID to calculate correlations for
            days: Number of days to analyze (default 30)
            
        Returns:
            List of correlation records to be inserted into meal_emotion_correlations
        """
        try:
            supabase = get_supabase()
            
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch meals
            meals_result = supabase.table("meals").select("*").eq(
                "user_id", user_id
            ).gte("meal_time", start_date.isoformat()).execute()
            
            if not meals_result.data:
                logger.info(f"No meals found for user {user_id}")
                return []
            
            # Fetch emotions
            emotions_result = supabase.table("emotion_logs").select("*").eq(
                "user_id", user_id
            ).gte("created_at", start_date.isoformat()).execute()
            
            if not emotions_result.data:
                logger.info(f"No emotions found for user {user_id}")
                return []
            
            # Calculate correlations
            correlations = []
            
            # Emotion scoring
            positive_emotions = ["joy", "happiness", "contentment", "calm", "love", "excitement", "gratitude"]
            negative_emotions = ["sadness", "anger", "anxiety", "fear", "disgust", "stress", "frustration"]
            
            for meal in meals_result.data:
                meal_time = datetime.fromisoformat(meal["meal_time"].replace("Z", "+00:00"))
                meal_id = meal["id"]
                
                # Look for emotions 1-4 hours after meal (digestion window)
                post_meal_start = meal_time + timedelta(hours=1)
                post_meal_end = meal_time + timedelta(hours=4)
                
                # Find relevant emotions
                for emotion in emotions_result.data:
                    emotion_time = datetime.fromisoformat(emotion["created_at"].replace("Z", "+00:00"))
                    
                    if post_meal_start <= emotion_time <= post_meal_end:
                        # Calculate time delta
                        time_delta_hours = (emotion_time - meal_time).total_seconds() / 3600
                        
                        # Calculate correlation score
                        emotion_type = emotion.get("emotion_type", "").lower()
                        confidence = emotion.get("confidence", 0.5)
                        
                        # Score: positive emotions get positive scores, negative get negative
                        correlation_score = 0.0
                        
                        if emotion_type in positive_emotions:
                            correlation_score = confidence
                        elif emotion_type in negative_emotions:
                            correlation_score = -confidence
                        else:
                            # Neutral emotions
                            correlation_score = 0.0
                        
                        # Store correlation
                        correlations.append({
                            "user_id": user_id,
                            "meal_id": meal_id,
                            "emotion_log_id": emotion["id"],
                            "correlation_score": correlation_score,
                            "time_delta_hours": time_delta_hours
                        })
            
            logger.info(f"Calculated {len(correlations)} meal-emotion correlations for user {user_id}")
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating meal correlations: {e}")
            return []
    
    @staticmethod
    def store_correlations(correlations: List[Dict]) -> int:
        """
        Store correlation records in database.
        
        Args:
            correlations: List of correlation dictionaries
            
        Returns:
            Number of records stored
        """
        try:
            if not correlations:
                return 0
            
            supabase = get_supabase()
            
            # Insert correlations
            result = supabase.table("meal_emotion_correlations").insert(correlations).execute()
            
            stored_count = len(result.data) if result.data else 0
            logger.info(f"Stored {stored_count} correlation records")
            
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing correlations: {e}")
            return 0
    
    @staticmethod
    def get_food_insights(user_id: str, limit: int = 10) -> Dict:
        """
        Get insights about which foods boost or drop mood.
        
        Args:
            user_id: User ID
            limit: Number of top foods to return
            
        Returns:
            Dictionary with mood_boosting and mood_dropping food lists
        """
        try:
            supabase = get_supabase()
            
            # Get all correlations for user
            correlations_result = supabase.table("meal_emotion_correlations") \
                .select("meal_id, correlation_score") \
                .eq("user_id", user_id) \
                .execute()
            
            if not correlations_result.data:
                return {
                    "mood_boosting": [],
                    "mood_dropping": [],
                    "total_analyzed": 0
                }
            
            # Get meals data
            meal_ids = list(set([c["meal_id"] for c in correlations_result.data]))
            
            meals_result = supabase.table("meals") \
                .select("id, meal_text, ingredients") \
                .in_("id", meal_ids) \
                .execute()
            
            # Create meal lookup
            meals_by_id = {m["id"]: m for m in meals_result.data}
            
            # Aggregate scores by meal text (food name)
            food_scores = defaultdict(lambda: {"scores": [], "count": 0})
            
            for corr in correlations_result.data:
                meal_id = corr["meal_id"]
                score = corr["correlation_score"]
                
                if meal_id in meals_by_id:
                    meal_text = meals_by_id[meal_id]["meal_text"]
                    food_scores[meal_text]["scores"].append(score)
                    food_scores[meal_text]["count"] += 1
            
            # Calculate average scores
            food_impacts = []
            
            for food, data in food_scores.items():
                if data["count"] >= 2:  # Need at least 2 occurrences for reliability
                    avg_score = sum(data["scores"]) / len(data["scores"])
                    food_impacts.append({
                        "food": food,
                        "avg_impact": avg_score,
                        "occurrences": data["count"]
                    })
            
            # Sort by impact
            food_impacts.sort(key=lambda x: x["avg_impact"], reverse=True)
            
            # Split into boosting and dropping
            mood_boosting = [
                {
                    "food": f["food"],
                    "impact_score": round(f["avg_impact"], 2),
                    "occurrences": f["occurrences"]
                }
                for f in food_impacts if f["avg_impact"] > 0.1
            ][:limit]
            
            mood_dropping = [
                {
                    "food": f["food"],
                    "impact_score": round(f["avg_impact"], 2),
                    "occurrences": f["occurrences"]
                }
                for f in food_impacts if f["avg_impact"] < -0.1
            ][:limit]
            
            # Reverse mood_dropping so worst foods are first
            mood_dropping.sort(key=lambda x: x["impact_score"])
            
            return {
                "mood_boosting": mood_boosting,
                "mood_dropping": mood_dropping,
                "total_analyzed": len(food_impacts)
            }
            
        except Exception as e:
            logger.error(f"Error getting food insights: {e}")
            return {
                "mood_boosting": [],
                "mood_dropping": [],
                "total_analyzed": 0
            }
    
    @staticmethod
    def run_correlation_analysis(user_id: str) -> Dict:
        """
        Run complete correlation analysis: calculate and store correlations.
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Summary of analysis
        """
        try:
            # Calculate correlations
            correlations = MealCorrelationService.calculate_meal_emotion_correlations(user_id)
            
            if not correlations:
                return {
                    "success": True,
                    "correlations_calculated": 0,
                    "correlations_stored": 0,
                    "message": "No correlations found"
                }
            
            # Clear old correlations for this user (optional - keep history or not)
            # supabase = get_supabase()
            # supabase.table("meal_emotion_correlations").delete().eq("user_id", user_id).execute()
            
            # Store new correlations
            stored = MealCorrelationService.store_correlations(correlations)
            
            return {
                "success": True,
                "correlations_calculated": len(correlations),
                "correlations_stored": stored,
                "message": f"Analyzed {stored} meal-emotion correlations"
            }
            
        except Exception as e:
            logger.error(f"Error running correlation analysis: {e}")
            return {
                "success": False,
                "correlations_calculated": 0,
                "correlations_stored": 0,
                "message": str(e)
            }
