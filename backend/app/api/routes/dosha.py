"""Dosha assessment and Ayurvedic intelligence routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.models.schemas import DoshaAssessmentRequest, DoshaAssessmentResponse
from app.services.dosha_service import DoshaService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/assess", response_model=DoshaAssessmentResponse)
async def assess_dosha(
    payload: DoshaAssessmentRequest,
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Submit dosha assessment quiz and calculate scores."""
    try:
        # Calculate dosha scores from answers
        scores = DoshaService.calculate_scores(payload.answers)
        
        # Prepare quiz responses for database storage
        quiz_responses = {
            "answers": [ans.model_dump() for ans in payload.answers],
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        # Insert assessment into database
        result = supabase.table("dosha_assessments").insert({
            "user_id": current_user_id,
            "vata_score": scores["vata_score"],
            "pitta_score": scores["pitta_score"],
            "kapha_score": scores["kapha_score"],
            "primary_dosha": scores["dominant_dosha"],
            "secondary_dosha": scores.get("secondary_dosha"),
            "quiz_responses": quiz_responses,
            "assessment_type": "full"
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save dosha assessment")
        
        logger.info(f"Dosha assessment saved for user {current_user_id}: {scores['dominant_dosha']}")
        
        # Return response matching frontend expectations
        return DoshaAssessmentResponse(
            vata_score=scores["vata_score"],
            pitta_score=scores["pitta_score"],
            kapha_score=scores["kapha_score"],
            dominant_dosha=scores["dominant_dosha"],
            primary_dosha=scores["dominant_dosha"],
            secondary_dosha=scores.get("secondary_dosha")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing dosha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_dosha(
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Get latest dosha assessment from database."""
    try:
        # Query most recent assessment for user
        result = supabase.table("dosha_assessments") \
            .select("*") \
            .eq("user_id", current_user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        
        if not result.data or len(result.data) == 0:
            # No assessment found - return default/empty state
            raise HTTPException(
                status_code=404, 
                detail="No dosha assessment found. Please complete the quiz first."
            )
        
        assessment = result.data[0]
        
        # Transform to match frontend expectations
        return {
            "vata_score": int(assessment["vata_score"]),
            "pitta_score": int(assessment["pitta_score"]),
            "kapha_score": int(assessment["kapha_score"]),
            "dominant_dosha": assessment["primary_dosha"],
            "primary_dosha": assessment["primary_dosha"],
            "secondary_dosha": assessment.get("secondary_dosha"),
            "assessment_date": assessment["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dosha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_recommendations(
    current_user_id: str = Depends(get_current_user_id),
    supabase=Depends(get_supabase)
):
    """Get personalized Ayurvedic recommendations from database based on dosha type."""
    try:
        # Get user's dominant dosha
        result = supabase.table("dosha_assessments") \
            .select("primary_dosha") \
            .eq("user_id", current_user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        
        dosha = result.data[0]["primary_dosha"] if result.data else "vata"
        primary_dosha = dosha.split("-")[0].lower()
        
        # Fetch recommendations from database grouped by category
        recommendations = {
            "diet": [],
            "lifestyle": [],
            "yoga": [],
            "meditation": []
        }
        
        for category in recommendations.keys():
            try:
                category_result = supabase.table("ayurveda_resources")\
                    .select("content")\
                    .eq("category", category)\
                    .contains("dosha_tags", [primary_dosha])\
                    .execute()
                
                if category_result.data:
                    recommendations[category] = [item["content"] for item in category_result.data]
            except Exception as e:
                logger.error(f"Error fetching {category} recommendations: {e}")
                recommendations[category] = []
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
