"""Aura visualization routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.models.schemas import AuraEntry
from app.services.aura_service import AuraService
from app.utils.database import get_supabase
from typing import List
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/today")
async def get_today_aura(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get today's aura - generates from emotions if not exists."""
    try:
        supabase = get_supabase()
        
        # Try to get existing aura for today
        result = supabase.table("aura_entries").select("*").eq(
            "user_id", current_user_id
        ).eq("date", date.today().isoformat()).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        # If no aura exists, generate one based on real emotion data
        aura_service = AuraService(supabase)
        aura_data = await aura_service.generate_daily_aura(current_user_id, date.today())
        return aura_data
        
    except Exception as e:
        logger.error(f"Error fetching today's aura: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch aura: {str(e)}")


@router.post("/generate")
async def generate_aura(
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate/regenerate today's aura based on recent emotions."""
    try:
        supabase = get_supabase()
        aura_service = AuraService(supabase)
        
        # Generate aura for today
        aura_data = await aura_service.generate_daily_aura(current_user_id, date.today())
        
        return aura_data
    except Exception as e:
        logger.error(f"Error generating aura: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate aura: {str(e)}")


@router.get("/timeline", response_model=List[AuraEntry])
async def get_aura_timeline(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 30
):
    """Get aura timeline."""
    supabase = get_supabase()
    
    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = supabase.table("aura_entries").select("*").eq(
            "user_id", current_user_id
        ).gte("date", since_date).order("date", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching aura timeline: {e}")
        raise
