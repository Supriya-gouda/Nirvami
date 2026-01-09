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
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit dosha assessment quiz and calculate scores."""
    try:
        # Use service role to bypass RLS (backend operations are already authenticated)
        from app.utils.database import get_supabase
        supabase = get_supabase(use_service_role=True)
        
        # Calculate dosha scores from answers
        scores = DoshaService.calculate_scores(payload.answers)
        
        # Prepare quiz responses for database storage
        quiz_responses = {
            "answers": [ans.model_dump() for ans in payload.answers],
            "submitted_at": datetime.utcnow().isoformat(),
            "result_type": scores["result_type"]  # Store single/dual/tri in JSONB
        }
        
        # Insert assessment into database
        result = supabase.table("dosha_assessments").insert({
            "user_id": current_user_id,
            "quiz_responses": quiz_responses,
            "vata_score": scores["vata_percent"],
            "pitta_score": scores["pitta_percent"],
            "kapha_score": scores["kapha_percent"],
            "primary_dosha": scores["primary_dosha"],
            "secondary_dosha": scores.get("secondary_dosha"),
            "assessment_type": "full"  # Use valid constraint value
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save dosha assessment")
        
        logger.info(f"Dosha assessment saved for user {current_user_id}: {scores['primary_dosha']} ({scores['result_type']})")
        
        # Return response matching schema
        return DoshaAssessmentResponse(
            vata_percent=scores["vata_percent"],
            pitta_percent=scores["pitta_percent"],
            kapha_percent=scores["kapha_percent"],
            primary_dosha=scores["primary_dosha"],
            secondary_dosha=scores.get("secondary_dosha"),
            result_type=scores["result_type"],
            dominant_dosha=scores["primary_dosha"]  # Backward compatibility
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing dosha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_dosha(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get latest dosha assessment from database."""
    try:
        # Use service role to bypass RLS
        from app.utils.database import get_supabase
        supabase = get_supabase(use_service_role=True)
        
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
            "id": assessment["id"],
            "user_id": assessment["user_id"],
            "vata_score": assessment["vata_score"],
            "pitta_score": assessment["pitta_score"],
            "kapha_score": assessment["kapha_score"],
            "dominant_dosha": assessment["primary_dosha"],
            "primary_dosha": assessment["primary_dosha"],
            "secondary_dosha": assessment.get("secondary_dosha"),
            "assessment_data": assessment.get("quiz_responses", {}),
            "assessment_date": assessment["created_at"],
            "created_at": assessment["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dosha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_recommendations(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get personalized Ayurvedic recommendations from database based on dosha type."""
    try:
        # Use service role to bypass RLS
        from app.utils.database import get_supabase
        supabase = get_supabase(use_service_role=True)
        
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

