"""Dosha assessment and Ayurvedic intelligence routes."""
from fastapi import APIRouter, Depends
from app.utils.auth import get_current_user_id
from app.utils.mock_data import get_mock_dosha
from app.models.schemas import DoshaQuizRequest, DoshaAssessment
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/latest")
async def get_latest_dosha(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get latest dosha assessment."""
    try:
        return get_mock_dosha()
    except Exception as e:
        logger.error(f"Error getting dosha: {e}")
        raise


@router.get("/recommendations")
async def get_recommendations(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get personalized Ayurvedic recommendations."""
    try:
        return {
            "diet": [
                "Favor warm, cooked foods",
                "Include healthy fats like ghee",
                "Avoid cold, raw foods"
            ],
            "lifestyle": [
                "Maintain regular routine",
                "Get adequate rest",
                "Practice gentle yoga"
            ],
            "yoga": [
                "Sun Salutations",
                "Forward bends",
                "Restorative poses"
            ],
            "meditation": [
                "Grounding meditation",
                "Body scan",
                "Breath awareness"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise
        raise
