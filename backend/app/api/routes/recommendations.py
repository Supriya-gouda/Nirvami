"""
Recommendations API routes
Provides endpoints for retrieving daily yoga and Ayurveda recommendations
"""
import logging
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.schemas import (
    Recommendation, 
    DailyRecommendationsResponse, 
    RecommendationCategory,
    RecommendationsBySource,
    RecommendationSource
)
from app.utils.auth import get_current_user_id
from app.services.recommendation_service import recommendation_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/yoga", response_model=List[Recommendation])
async def get_yoga_recommendations(
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get yoga recommendations for a specific date (defaults to today)
    """
    try:
        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get yoga recommendations
        recommendations = await recommendation_service.get_recommendations_by_category(
            user_id=current_user_id,
            category=RecommendationCategory.YOGA,
            target_date=target_date
        )
        
        logger.info(f"Retrieved {len(recommendations)} yoga recommendations for user {current_user_id} on {target_date}")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching yoga recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ayurveda", response_model=List[Recommendation])
async def get_ayurveda_recommendations(
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get Ayurveda recommendations for a specific date (defaults to today)
    """
    try:
        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get ayurveda recommendations
        recommendations = await recommendation_service.get_recommendations_by_category(
            user_id=current_user_id,
            category=RecommendationCategory.AYURVEDA,
            target_date=target_date
        )
        
        logger.info(f"Retrieved {len(recommendations)} Ayurveda recommendations for user {current_user_id} on {target_date}")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Ayurveda recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/lifestyle", response_model=List[Recommendation])
async def get_lifestyle_recommendations(
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get lifestyle recommendations for a specific date (defaults to today)
    """
    try:
        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get lifestyle recommendations
        recommendations = await recommendation_service.get_recommendations_by_category(
            user_id=current_user_id,
            category=RecommendationCategory.LIFESTYLE,
            target_date=target_date
        )
        
        logger.info(f"Retrieved {len(recommendations)} lifestyle recommendations for user {current_user_id} on {target_date}")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lifestyle recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/all", response_model=DailyRecommendationsResponse)
async def get_all_daily_recommendations(
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get all recommendations for a specific date, grouped by category
    """
    try:
        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get all daily recommendations
        daily_recs = await recommendation_service.get_daily_recommendations(
            user_id=current_user_id,
            target_date=target_date
        )
        
        total_count = sum([
            len(daily_recs.yoga),
            len(daily_recs.ayurveda),
            len(daily_recs.lifestyle),
            len(daily_recs.sleep),
            len(daily_recs.breathing),
            len(daily_recs.meditation),
            len(daily_recs.diet)
        ])
        
        logger.info(f"Retrieved {total_count} total recommendations for user {current_user_id} on {target_date}")
        return daily_recs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching daily recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/by-category/{category}", response_model=List[Recommendation])
async def get_recommendations_by_category(
    category: RecommendationCategory,
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get recommendations for any specific category and date
    """
    try:
        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Get recommendations for the category
        recommendations = await recommendation_service.get_recommendations_by_category(
            user_id=current_user_id,
            category=category,
            target_date=target_date
        )
        
        logger.info(f"Retrieved {len(recommendations)} {category.value} recommendations for user {current_user_id} on {target_date}")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching {category} recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/grouped-by-source", response_model=RecommendationsBySource)
async def get_recommendations_grouped_by_source(
    category: Optional[RecommendationCategory] = Query(None, description="Filter by category"),
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get recommendations grouped by source (chat, device, system) for easier display
    """
    try:
        from app.utils.database import get_supabase
        
        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Build query
        supabase = get_supabase()
        query = supabase.table("recommendations")\
            .select("*")\
            .eq("user_id", current_user_id)\
            .eq("date", target_date.isoformat())
        
        # Add category filter if provided
        if category:
            query = query.eq("category", category.value)
        
        result = query.order("created_at", desc=True).execute()
        
        # Group by source
        grouped = {"chat": [], "device": [], "system": []}
        
        for rec_data in result.data or []:
            # Safe timestamp parsing
            try:
                created_at_str = rec_data["created_at"]
                if '+' in created_at_str and '.' in created_at_str:
                    main_part, micro_tz_part = created_at_str.split('.')
                    if '+' in micro_tz_part:
                        micro_part, tz_part = micro_tz_part.split('+')
                        micro_part = micro_part[:6].ljust(6, '0')
                        created_at_str = f"{main_part}.{micro_part}+{tz_part}"
                created_at = datetime.fromisoformat(created_at_str)
            except ValueError:
                created_at = datetime.now()
            
            rec = Recommendation(
                id=rec_data["id"],
                user_id=rec_data["user_id"],
                date=datetime.fromisoformat(rec_data["date"]).date(),
                source=RecommendationSource(rec_data["source"]),
                category=RecommendationCategory(rec_data["category"]),
                title=rec_data["title"],
                content=rec_data["content"],
                created_at=created_at,
                meta=rec_data.get("meta", {})
            )
            
            source = rec.source.value if hasattr(rec.source, 'value') else rec.source
            if source in grouped:
                grouped[source].append(rec)
        
        logger.info(f"Retrieved recommendations grouped by source for user {current_user_id} on {target_date}")
        
        return RecommendationsBySource(
            chat=grouped["chat"],
            device=grouped["device"],
            system=grouped["system"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recommendations by source: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")