from fastapi import APIRouter, Depends, HTTPException, Body
from datetime import date, datetime, time
from typing import Optional, List
from pydantic import BaseModel
import json
import logging

from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase

router = APIRouter(prefix="/dinacharya", tags=["dinacharya"])
logger = logging.getLogger(__name__)


# ==================== Pydantic Models ====================

class DailyRoutineItem(BaseModel):
    time: str  # HH:MM format
    activity: str
    notes: Optional[str] = None


class DinachariyaLogRequest(BaseModel):
    log_date: Optional[date] = None
    routines: List[DailyRoutineItem] = []
    stress_level: Optional[int] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    sleep_hours: Optional[float] = None
    notes: Optional[str] = None


class MealLogRequest(BaseModel):
    meal_type: str
    meal_time: Optional[str] = None
    foods: List[str]
    notes: Optional[str] = None


# ==================== Endpoints ====================

@router.get("/today")
async def get_today_dinacharya(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get today's Dinacharya data including routines, meals, and wellness metrics
    """
    supabase = get_supabase()
    today = str(date.today())
    
    try:
        # Get today's routines
        routines_result = supabase.table("daily_routines").select("*").eq(
            "user_id", current_user_id
        ).eq("date", today).order("time").execute()
        
        # Get today's meals
        meals_result = supabase.table("meals").select("*").eq(
            "user_id", current_user_id
        ).gte("meal_time", f"{today}T00:00:00").lte("meal_time", f"{today}T23:59:59").order("meal_time").execute()
        
        # Get today's wellness score (if exists)
        wellness_result = supabase.table("wellness_scores").select("*").eq(
            "user_id", current_user_id
        ).eq("date", today).execute()
        
        # Get latest emotion logs for today
        emotion_result = supabase.table("emotion_logs").select("*").eq(
            "user_id", current_user_id
        ).gte("created_at", f"{today}T00:00:00").order("created_at", desc=True).limit(10).execute()
        
        # Get wearable data for today
        wearable_result = supabase.table("wearable_snapshots").select("*").eq(
            "user_id", current_user_id
        ).eq("date", today).execute()
        
        return {
            "date": today,
            "routines": routines_result.data or [],
            "meals": meals_result.data or [],
            "wellness": wellness_result.data[0] if wellness_result.data else None,
            "emotions": emotion_result.data or [],
            "wearable": wearable_result.data[0] if wearable_result.data else None,
            "ai_suggestions": None  # Will be populated after analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting today's dinacharya: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/log")
async def log_dinacharya(
    data: DinachariyaLogRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Log or update today's Dinacharya including routines and wellness metrics
    """
    supabase = get_supabase(use_service_role=True)
    log_date = data.log_date or date.today()
    log_date_str = str(log_date)
    
    try:
        # Save/update daily routines
        routine_ids = []
        for routine in data.routines:
            routine_data = {
                "user_id": current_user_id,
                "date": log_date_str,
                "time": routine.time,
                "activity": routine.activity,
                "notes": routine.notes
            }
            
            # Check if routine already exists for this time
            existing = supabase.table("daily_routines").select("id").eq(
                "user_id", current_user_id
            ).eq("date", log_date_str).eq("time", routine.time).execute()
            
            if existing.data:
                # Update existing routine
                result = supabase.table("daily_routines").update(routine_data).eq(
                    "id", existing.data[0]["id"]
                ).execute()
            else:
                # Insert new routine
                result = supabase.table("daily_routines").insert(routine_data).execute()
            
            if result.data:
                routine_ids.append(result.data[0]["id"])
        
        # Update wearable snapshot with wellness metrics
        wearable_data = {
            "user_id": current_user_id,
            "date": log_date_str,
            "source": "manual",
            "stress_level": data.stress_level,
            "sleep_hours": data.sleep_hours
        }
        
        # Upsert wearable snapshot
        existing_wearable = supabase.table("wearable_snapshots").select("id").eq(
            "user_id", current_user_id
        ).eq("date", log_date_str).execute()
        
        if existing_wearable.data:
            wearable_result = supabase.table("wearable_snapshots").update(wearable_data).eq(
                "id", existing_wearable.data[0]["id"]
            ).execute()
        else:
            wearable_result = supabase.table("wearable_snapshots").insert(wearable_data).execute()
        
        # Generate AI suggestions based on the data
        ai_suggestions = await generate_dinacharya_suggestions(
            current_user_id, 
            log_date_str, 
            data
        )
        
        return {
            "success": True,
            "routines_saved": len(routine_ids),
            "wellness_updated": True,
            "ai_suggestions": ai_suggestions,
            "message": "Dinacharya logged successfully"
        }
        
    except Exception as e:
        logger.error(f"Error logging dinacharya: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_dinacharya_history(
    days: int = 7,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get Dinacharya history for the last N days
    """
    supabase = get_supabase()
    
    try:
        # Calculate date range
        end_date = date.today()
        from datetime import timedelta
        start_date = end_date - timedelta(days=days)
        
        # Get routines for date range
        routines_result = supabase.table("daily_routines").select("*").eq(
            "user_id", current_user_id
        ).gte("date", str(start_date)).lte("date", str(end_date)).order("date", desc=True).order("time").execute()
        
        # Group by date
        grouped_data = {}
        for routine in (routines_result.data or []):
            routine_date = routine["date"]
            if routine_date not in grouped_data:
                grouped_data[routine_date] = {
                    "date": routine_date,
                    "routines": [],
                    "meals": [],
                    "wellness": None
                }
            grouped_data[routine_date]["routines"].append(routine)
        
        # Get meals for date range
        meals_result = supabase.table("meals").select("*").eq(
            "user_id", current_user_id
        ).gte("meal_time", f"{start_date}T00:00:00").lte("meal_time", f"{end_date}T23:59:59").order("meal_time").execute()
        
        for meal in (meals_result.data or []):
            meal_date = meal["meal_time"][:10]  # Extract date from timestamp
            if meal_date in grouped_data:
                grouped_data[meal_date]["meals"].append(meal)
        
        # Get wellness scores for date range
        wellness_result = supabase.table("wellness_scores").select("*").eq(
            "user_id", current_user_id
        ).gte("date", str(start_date)).lte("date", str(end_date)).execute()
        
        for wellness in (wellness_result.data or []):
            wellness_date = wellness["date"]
            if wellness_date in grouped_data:
                grouped_data[wellness_date]["wellness"] = wellness
        
        # Convert to list and sort by date descending
        history = list(grouped_data.values())
        history.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "history": history,
            "days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting dinacharya history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class AnalyzeRequest(BaseModel):
    target_date: Optional[str] = None

@router.post("/analyze")
async def analyze_dinacharya(
    request: AnalyzeRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Analyze Dinacharya and generate AI suggestions
    """
    analysis_date = request.target_date or str(date.today())
    
    try:
        logger.info(f"[ANALYZE] Starting analysis for user {current_user_id} on date {analysis_date}")
        
        # Generate suggestions
        suggestions = await generate_dinacharya_suggestions(
            current_user_id,
            analysis_date,
            None  # Will fetch data internally
        )
        
        logger.info(f"[ANALYZE] Successfully generated suggestions for {analysis_date}")
        
        return {
            "date": analysis_date,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Error analyzing dinacharya: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Helper Functions ====================

async def generate_dinacharya_suggestions(
    user_id: str, 
    log_date: str, 
    log_data: Optional[DinachariyaLogRequest]
) -> dict:
    """
    Generate comprehensive AI-powered schedule analysis using Gemini Flash 1.5/2.0
    Provides 8 categories of recommendations based on Ayurvedic + modern productivity science
    """
    from app.services.gemini_chatbot import get_gemini_response
    
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Fetch routine data
        routines = supabase.table("daily_routines").select("*").eq(
            "user_id", user_id
        ).eq("date", log_date).order("time").execute()
        
        # Fetch wellness data
        wellness = supabase.table("wellness_scores").select("*").eq(
            "user_id", user_id
        ).eq("date", log_date).execute()
        
        # Fetch wearable data
        wearable = supabase.table("wearable_snapshots").select("*").eq(
            "user_id", user_id
        ).eq("date", log_date).execute()
        
        # Fetch dosha assessment
        dosha = supabase.table("dosha_assessments").select("*").eq(
            "user_id", user_id
        ).order("assessment_date", desc=True).limit(1).execute()
        
        # Build detailed routine list
        routine_items = []
        for r in (routines.data or []):
            notes = f" ({r['notes']})" if r.get('notes') else ""
            routine_items.append(f"{r['time']} - {r['activity']}{notes}")
        
        wellness_data = wellness.data[0] if wellness.data else None
        wearable_data = wearable.data[0] if wearable.data else None
        dosha_data = dosha.data[0] if dosha.data else None
        dosha_type = dosha_data.get('primary_dosha', 'Unknown').lower() if dosha_data else 'unknown'
        
        # Build comprehensive analysis prompt focused on actual routine problems
        prompt = f"""You are an expert Ayurvedic wellness consultant analyzing a person's daily routine.

**DAILY SCHEDULE for {log_date}**:
{chr(10).join(routine_items) if routine_items else 'No routines logged'}

**Dosha Type**: {dosha_type.upper()}
**Wellness Metrics**:
- Stress: {log_data.stress_level if log_data and log_data.stress_level else wearable_data.get('stress_level') if wearable_data else 'Unknown'}/10
- Energy: {log_data.energy_level if log_data and log_data.energy_level else 'Unknown'}/10
- Sleep Quality: {log_data.sleep_quality if log_data and log_data.sleep_quality else 'Unknown'}/10
- Sleep Hours: {log_data.sleep_hours if log_data and log_data.sleep_hours else wearable_data.get('sleep_hours') if wearable_data else 'Unknown'}

**YOUR TASK**:
1. Carefully analyze the ACTUAL schedule above
2. Identify SPECIFIC problems (gaps, poor timing, missing activities, imbalances)
3. Provide TARGETED suggestions ONLY for the problems you identified
4. Score the routine (0-100) based on Ayurvedic principles

**ANALYSIS CATEGORIES** (only suggest if there's a problem):
- Sleep/Wake: Check sleep hours (<7 hrs = problem), late bedtime, irregular wake times
- Breaks: Long work blocks without breaks (>90 min), no recovery time
- Movement: Missing exercise, sedentary lifestyle, poor timing
- Meals: Irregular timing, skipped meals, late dinner (after 8 PM)
- Productivity: High-focus work in wrong time slots, poor task sequencing
- Stress Management: Missing mindfulness/relaxation, overloaded schedule
- Dosha Balance: Activities not aligned with dosha type
- Rescheduling: Specific tasks that should be moved to better times

**CRITICAL**: Return ONLY valid JSON with NO markdown, NO code blocks, NO extra text.

{{
  "routine_score": 75,
  "overall_assessment": "1-2 sentence summary of main strengths and weaknesses",
  "sleep_recommendations": ["Problem: Late bedtime at 11 PM. Suggestion: Shift to 10 PM for better rest"],
  "break_recommendations": ["Problem: 3-hour study block without breaks. Add 5-min breaks every hour"],
  "movement_recommendations": ["Problem: No exercise logged. Add 20-min morning walk at 6:30 AM"],
  "meal_recommendations": ["Problem: Dinner at 9 PM too late. Move to 7 PM for better digestion"],
  "productivity_recommendations": ["Problem: Study at 8 PM when tired. Move to 7 AM for peak focus"],
  "stress_recommendations": ["Problem: No relaxation activities. Add 10-min meditation at 8 PM"],
  "dosha_recommendations": ["Based on {dosha_type}: Add grounding activities in morning"],
  "rescheduling_suggestions": [
    {{"task": "Specific activity name", "current_time": "HH:MM", "suggested_time": "HH:MM", "reason": "Why this is better"}}
  ],
  "missing_elements": ["Activities that should be added"],
  "optimal_schedule": {{
    "wake_time": "HH:MM",
    "sleep_time": "HH:MM"
  }}
}}"""
        
        # Get AI response from Gemini Flash
        logger.info(f"[AI_ANALYSIS] Sending prompt to Gemini (routines: {len(routine_items)})")
        
        system_instruction = """You are a JSON-only API. You MUST return ONLY valid JSON with no markdown formatting, 
no code blocks, no explanatory text, and no additional characters. Your entire response must be parseable by json.loads()."""
        
        ai_response = await get_gemini_response(prompt, system_instruction=system_instruction, temperature=0.7)
        
        logger.info(f"[AI_ANALYSIS] Received response length: {len(ai_response)} chars")
        logger.debug(f"[AI_ANALYSIS] Raw response: {ai_response[:500]}...")
        
        # Parse JSON from response - try multiple strategies
        import re
        
        # Strategy 1: Remove markdown code blocks
        cleaned_response = re.sub(r'```(?:json)?\s*|\s*```', '', ai_response)
        
        # Strategy 2: Find JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_response, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group()
                logger.debug(f"[AI_ANALYSIS] Extracted JSON: {json_str[:200]}...")
                analysis = json.loads(json_str)
                
                logger.info(f"[AI_ANALYSIS] Successfully parsed - Score: {analysis.get('routine_score', 'N/A')}")
                
                return {
                    "routine_score": analysis.get("routine_score", 50),
                    "overall_assessment": analysis.get("overall_assessment", "Analysis generated successfully"),
                    "sleep_recommendations": analysis.get("sleep_recommendations", []),
                    "break_recommendations": analysis.get("break_recommendations", []),
                    "movement_recommendations": analysis.get("movement_recommendations", []),
                    "meal_recommendations": analysis.get("meal_recommendations", []),
                    "productivity_recommendations": analysis.get("productivity_recommendations", []),
                    "stress_recommendations": analysis.get("stress_recommendations", []),
                    "dosha_recommendations": analysis.get("dosha_recommendations", []),
                    "rescheduling_suggestions": analysis.get("rescheduling_suggestions", []),
                    "missing_elements": analysis.get("missing_elements", []),
                    "optimal_schedule": analysis.get("optimal_schedule", {}),
                    "generated_at": datetime.now().isoformat()
                }
            except json.JSONDecodeError as je:
                logger.error(f"[AI_ANALYSIS] JSON parse error: {je}")
                logger.error(f"[AI_ANALYSIS] Failed to parse: {json_str[:300]}...")
        
        # If parsing failed, log the full response for debugging
        logger.error(f"[AI_ANALYSIS] Could not extract valid JSON from response")
        logger.error(f"[AI_ANALYSIS] Full response: {ai_response}")
        
        return {
            "routine_score": 50,
            "overall_assessment": "Could not parse AI analysis. Please try again.",
            "sleep_recommendations": [],
            "break_recommendations": [],
            "movement_recommendations": [],
            "meal_recommendations": [],
            "productivity_recommendations": [],
            "stress_recommendations": [],
            "dosha_recommendations": [],
            "rescheduling_suggestions": [],
            "missing_elements": [],
            "optimal_schedule": {},
            "error": "JSON parsing failed",
            "generated_at": datetime.now().isoformat()
        }
            
    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}", exc_info=True)
        return {
            "routine_score": 50,
            "overall_assessment": "Error generating analysis",
            "sleep_recommendations": [],
            "break_recommendations": [],
            "movement_recommendations": [],
            "meal_recommendations": [],
            "productivity_recommendations": [],
            "stress_recommendations": [],
            "dosha_recommendations": [],
            "rescheduling_suggestions": [],
            "missing_elements": [],
            "optimal_schedule": {},
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }
