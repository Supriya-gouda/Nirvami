"""Meal tracking routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import CreateMealRequest, Meal
from app.services.meal_service import MealService
from app.services.meal_mood_correlation_service import MealMoodCorrelationService
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
meal_service = MealService()
correlation_service = MealMoodCorrelationService()


@router.post("/log")
async def log_meal(
    meal_data: Dict[str, Any] = Body(...),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Log a meal with Ayurvedic analysis
    
    Expected meal_data:
    {
        "meal_text": "Grilled chicken with vegetables",
        "meal_type": "lunch", 
        "meal_time": "2025-12-05T13:30:00Z",
        "notes": "Felt energetic after this meal"
    }
    """
    try:
        logger.info(f"Logging meal for user {current_user_id}")
        
        # Validate required fields
        if not meal_data.get('meal_text'):
            raise HTTPException(status_code=400, detail="meal_text is required")
        
        # Log meal and get analysis
        result = await meal_service.log_meal(current_user_id, meal_data)
        
        return {
            "success": True,
            "message": "Meal logged and analyzed successfully",
            "meal_id": result["id"],
            "meal": result,
            "analysis": result.get("analysis", {})
        }
        
    except Exception as e:
        logger.error(f"Error logging meal: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging meal: {str(e)}")


@router.get("/today")
async def get_today_meals(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Get today's meals for the meal log"""
    try:
        logger.info(f"Getting today's meals for user {current_user_id}")
        
        # Get today's date range
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.min.time())
        end_time = datetime.combine(today, datetime.max.time())
        
        supabase = get_supabase(use_service_role=True)
        response = supabase.table('meals').select('*')\
            .eq('user_id', current_user_id)\
            .gte('meal_time', start_time.date().isoformat())\
            .lt('meal_time', (start_time.date() + timedelta(days=1)).isoformat())\
            .order('meal_time', desc=False).execute()
        
        meals = response.data
        
        # Group by meal type
        meals_by_type = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': []
        }
        
        for meal in meals:
            meal_type = meal.get('meal_type', 'snack')
            if meal_type in meals_by_type:
                meals_by_type[meal_type].append(meal)
        
        return {
            "date": today.isoformat(),
            "meals": meals_by_type,
            "total_meals": len(meals)
        }
        
    except Exception as e:
        logger.error(f"Error getting today's meals: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting today's meals: {str(e)}")


@router.get("/weekly-counts")
async def get_weekly_meal_counts(
    current_user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    """Get meal counts for the last 7 days"""
    try:
        logger.info(f"Getting weekly meal counts for user {current_user_id}")
        
        # Get last 7 days
        today = datetime.now().date()
        week_data = []
        
        supabase = get_supabase(use_service_role=True)
        
        for i in range(7):
            day_date = today - timedelta(days=6-i)
            start_time = datetime.combine(day_date, datetime.min.time())
            end_time = datetime.combine(day_date, datetime.max.time())
            
            response = supabase.table('meals').select('*')\
                .eq('user_id', current_user_id)\
                .gte('meal_time', start_time.date().isoformat())\
                .lt('meal_time', (start_time.date() + timedelta(days=1)).isoformat())\
                .execute()
            
            meals = response.data
            
            # Count by meal type
            meal_counts = {
                'breakfast': len([m for m in meals if m.get('meal_type') == 'breakfast']),
                'lunch': len([m for m in meals if m.get('meal_type') == 'lunch']),
                'dinner': len([m for m in meals if m.get('meal_type') == 'dinner']),
                'snack': len([m for m in meals if m.get('meal_type') == 'snack']),
            }
            
            # Format day name
            if i == 6:  # Today
                day_name = "Today"
            elif i == 5:  # Yesterday  
                day_name = "Yesterday"
            else:
                day_name = day_date.strftime('%a')  # Mon, Tue, etc.
            
            week_data.append({
                'day': day_name,
                'date': day_date.isoformat(),
                'breakfast': meal_counts['breakfast'],
                'lunch': meal_counts['lunch'],
                'dinner': meal_counts['dinner'],
                'snack': meal_counts['snack'],
                'total': sum(meal_counts.values())
            })
        
        return week_data
        
    except Exception as e:
        logger.error(f"Error getting weekly meal counts: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting weekly meal counts: {str(e)}")


@router.get("/debug/all")
async def debug_all_meals(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Debug endpoint to see all meals for user"""
    try:
        supabase = get_supabase(use_service_role=True)
        response = supabase.table('meals').select('*')\
            .eq('user_id', current_user_id)\
            .order('created_at', desc=True).execute()
        
        return {
            "user_id": current_user_id,
            "total_meals": len(response.data),
            "meals": response.data
        }
    except Exception as e:
        logger.error(f"Error getting all meals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weekly-pattern")
async def get_weekly_meal_pattern(
    weeks: int = Query(4, ge=1, le=12),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Get weekly meal patterns and analytics"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        supabase = get_supabase(use_service_role=True)
        response = supabase.table('meals').select('*')\
            .eq('user_id', current_user_id)\
            .gte('meal_time', start_date.isoformat())\
            .lte('meal_time', end_date.isoformat())\
            .order('meal_time', desc=False).execute()
        
        meals = response.data
        
        # Group meals by week and analyze patterns
        weekly_data = []
        for i in range(weeks):
            week_start = end_date - timedelta(weeks=weeks-i-1, days=end_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            week_meals = [m for m in meals if week_start <= datetime.fromisoformat(m['meal_time'].replace('Z', '+00:00')).date() <= week_end]
            
            weekly_data.append({
                'week': f"Week {i+1}",
                'start_date': week_start.isoformat(),
                'end_date': week_end.isoformat(),
                'total_meals': len(week_meals),
                'breakfast_count': len([m for m in week_meals if m['meal_type'] == 'breakfast']),
                'lunch_count': len([m for m in week_meals if m['meal_type'] == 'lunch']),
                'dinner_count': len([m for m in week_meals if m['meal_type'] == 'dinner']),
                'snack_count': len([m for m in week_meals if m['meal_type'] == 'snack']),
                'avg_calories': sum(m.get('calories', 0) for m in week_meals) / len(week_meals) if week_meals else 0
            })
        
        return {
            "pattern": weekly_data,
            "total_weeks": weeks,
            "total_meals_analyzed": len(meals)
        }
        
    except Exception as e:
        logger.error(f"Error getting weekly pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_meal_history(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    """Get meal history for a date range"""
    try:
        logger.info(f"Getting meal history for user {current_user_id} from {start_date} to {end_date}")
        
        # Parse dates
        try:
            start_dt = datetime.fromisoformat(start_date + "T00:00:00")
            end_dt = datetime.fromisoformat(end_date + "T23:59:59")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        supabase = get_supabase()
        response = supabase.table('meals').select('*')\
            .eq('user_id', current_user_id)\
            .gte('meal_time', start_dt.isoformat())\
            .lte('meal_time', end_dt.isoformat())\
            .order('meal_time', desc=True).execute()
        
        meals = response.data
        logger.info(f"Retrieved {len(meals)} meals for user {current_user_id}")
        
        return meals
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting meal history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting meal history: {str(e)}")


@router.get("/weekly-pattern")
async def get_weekly_meal_pattern(
    weeks: int = Query(4, description="Number of weeks to analyze"),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Get weekly meal pattern for charts"""
    try:
        logger.info(f"Getting weekly meal pattern for user {current_user_id} over {weeks} weeks")
        
        pattern = await meal_service.get_weekly_meal_pattern(current_user_id)
        
        return {
            "pattern": pattern,
            "weeks_analyzed": weeks,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting weekly meal pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting weekly meal pattern: {str(e)}")


@router.get("/ayurveda-guidelines")
async def get_meal_ayurveda_guidelines(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)"),
    current_user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    """Get Ayurvedic guidelines from meal analysis (separate from main recommendations)"""
    try:
        logger.info(f"Getting meal Ayurveda guidelines for user {current_user_id}")
        
        # Use today's date if not provided
        if date is None:
            target_date = datetime.now().date()
        else:
            try:
                target_date = datetime.fromisoformat(date).date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        supabase = get_supabase()
        response = supabase.table('meal_ayurveda_guidelines').select('*')\
            .eq('user_id', current_user_id)\
            .gte('created_at', target_date.isoformat())\
            .lte('created_at', (target_date + timedelta(days=1)).isoformat())\
            .order('created_at', desc=True).execute()
        
        guidelines = response.data
        logger.info(f"Retrieved {len(guidelines)} Ayurveda guidelines for user {current_user_id}")
        
        return guidelines
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Ayurveda guidelines: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting Ayurveda guidelines: {str(e)}")


@router.get("/daily-analysis")
async def get_daily_meal_analysis(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Get comprehensive Ayurvedic analysis of all today's meals"""
    try:
        logger.info(f"Getting daily meal analysis for user {current_user_id}")
        
        analysis = await meal_service.get_daily_meal_analysis(current_user_id)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting daily meal analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting daily meal analysis: {str(e)}")


@router.get("/recipe-suggestions")
async def get_meal_recipe_suggestions(
    dosha: Optional[str] = Query(None, description="Target dosha (vata, pitta, kapha)"),
    meal_type: Optional[str] = Query(None, description="Meal type (breakfast, lunch, dinner, snack)"),
    current_user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    """Get personalized recipe suggestions"""
    try:
        logger.info(f"Getting recipe suggestions for user {current_user_id}")
        
        supabase = get_supabase()
        query = supabase.table('meal_recipe_suggestions').select('*').eq('user_id', current_user_id)
        
        if dosha:
            query = query.contains('dosha_balance_tags', [dosha])
        
        if meal_type:
            query = query.eq('meal_type', meal_type)
        
        response = query.order('created_at', desc=True).limit(10).execute()
        
        suggestions = response.data
        logger.info(f"Retrieved {len(suggestions)} recipe suggestions for user {current_user_id}")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting recipe suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recipe suggestions: {str(e)}")


@router.get("/mood-correlations")
async def get_meal_mood_correlations(
    current_user_id: str = Depends(get_current_user_id),
    days: int = Query(30, description="Number of days to analyze")
) -> Dict[str, Any]:
    """Get meal-mood correlation analysis"""
    try:
        logger.info(f"Getting meal-mood correlations for user {current_user_id} over {days} days")
        
        # Calculate correlations
        correlations = await correlation_service.calculate_meal_mood_correlations(current_user_id, days)
        
        # Get insights
        insights = await correlation_service.get_meal_mood_insights(current_user_id)
        
        return {
            "correlations": [
                {
                    "ingredient": corr.meal_ingredient,
                    "meal_type": corr.meal_type,
                    "positive_correlation": corr.positive_correlation,
                    "negative_correlation": corr.negative_correlation,
                    "strength": corr.correlation_strength,
                    "sample_size": corr.sample_size,
                    "insights": corr.insights
                }
                for corr in correlations
            ],
            "insights": insights,
            "analyzed_days": days,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting meal-mood correlations: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting meal-mood correlations: {str(e)}")


@router.get("/mood-insights")
async def get_meal_mood_insights(
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Get personalized meal-mood insights"""
    try:
        logger.info(f"Getting meal-mood insights for user {current_user_id}")
        
        insights = await correlation_service.get_meal_mood_insights(current_user_id, meal_type)
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting meal-mood insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting meal-mood insights: {str(e)}")


@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: int,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Delete a meal entry"""
    try:
        logger.info(f"Deleting meal {meal_id} for user {current_user_id}")
        
        supabase = get_supabase()
        
        # Verify meal belongs to user
        response = supabase.table('meals').select('id').eq('id', meal_id).eq('user_id', current_user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        # Delete meal
        supabase.table('meals').delete().eq('id', meal_id).execute()
        
        return {"success": True, "message": "Meal deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting meal: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting meal: {str(e)}")
