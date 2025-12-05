"""Daily routine tracking routes."""
from fastapi import APIRouter, Depends, HTTPException, Body
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from pydantic import BaseModel
from datetime import date, time, datetime
from typing import List, Optional, Dict, Any
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


class RoutineEntryRequest(BaseModel):
    date: str  # Changed to string to accept "YYYY-MM-DD"
    time: str  # Changed to string to accept "HH:MM"
    activity: str
    notes: Optional[str] = None


class RoutineEntry(BaseModel):
    id: str
    user_id: str
    date: date
    time: time
    activity: str
    notes: Optional[str] = None
    created_at: datetime


@router.post("/entry")
async def add_routine_entry(
    req: RoutineEntryRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Add a daily routine entry."""
    supabase = get_supabase(use_service_role=True)  # Use service role to bypass RLS
    
    try:
        logger.info(f"[ROUTINE] ===== NEW REQUEST =====")
        logger.info(f"[ROUTINE] User ID: {current_user_id}")
        logger.info(f"[ROUTINE] Date: {req.date} (type: {type(req.date)})")
        logger.info(f"[ROUTINE] Time: {req.time} (type: {type(req.time)})")
        logger.info(f"[ROUTINE] Activity: {req.activity}")
        logger.info(f"[ROUTINE] Notes: {req.notes}")
        
        # Prepare entry data - strings are fine for Supabase
        entry_data = {
            "user_id": current_user_id,
            "date": req.date,  # Already a string in YYYY-MM-DD format
            "time": req.time,  # Already a string in HH:MM format
            "activity": req.activity,
            "notes": req.notes
        }
        
        logger.info(f"[ROUTINE] Inserting data: {entry_data}")
        result = supabase.table("daily_routines").insert(entry_data).execute()
        
        logger.info(f"[ROUTINE] Supabase response: {result}")
        logger.info(f"[ROUTINE] Supabase data: {result.data}")
        
        if result.data and len(result.data) > 0:
            logger.info(f"✅ [ROUTINE] SUCCESS! Entry ID: {result.data[0].get('id')}")
            return result.data[0]
        else:
            logger.error(f"❌ [ROUTINE] No data returned from Supabase")
            logger.error(f"[ROUTINE] Full result: {result}")
            raise HTTPException(status_code=500, detail="Failed to save routine entry - no data returned")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [ROUTINE] EXCEPTION: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save routine entry: {str(e)}")


@router.get("/entries", response_model=List[RoutineEntry])
async def get_routine_entries(
    current_user_id: str = Depends(get_current_user_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: int = 7
):
    """Get routine entries for user."""
    supabase = get_supabase(use_service_role=True)  # Use service role to bypass RLS
    
    try:
        # Use start_date if provided, otherwise calculate from days
        if start_date:
            since_date = start_date
        else:
            from datetime import timedelta
            since_date = (date.today() - timedelta(days=days)).isoformat()
        
        query = supabase.table("daily_routines").select("*").eq(
            "user_id", current_user_id
        ).gte("date", since_date)
        
        # Add end_date filter if provided
        if end_date:
            query = query.lte("date", end_date)
        
        result = query.order("date", desc=True).order("time", desc=True).execute()
        
        logger.info(f"Retrieved {len(result.data)} routine entries for user {current_user_id}")
        return result.data
        
    except Exception as e:
        logger.error(f"Error fetching routine entries: {e}", exc_info=True)
        return []


@router.delete("/entry/{entry_id}")
async def delete_routine_entry(
    entry_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete a routine entry."""
    supabase = get_supabase(use_service_role=True)  # Use service role to bypass RLS
    
    try:
        result = supabase.table("daily_routines").delete().eq(
            "id", entry_id
        ).eq("user_id", current_user_id).execute()
        
        logger.info(f"Deleted routine entry {entry_id} for user {current_user_id}")
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Error deleting routine entry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete routine entry: {str(e)}")
