"""Daily routine tracking routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from pydantic import BaseModel
from datetime import date, time, datetime
from typing import List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


class RoutineEntryRequest(BaseModel):
    date: date
    time: time
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
    supabase = get_supabase()
    
    try:
        entry_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user_id,
            "date": req.date.isoformat(),
            "time": req.time.isoformat(),
            "activity": req.activity,
            "notes": req.notes,
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"[ROUTINE] user={current_user_id}, activity={req.activity}, date={req.date}")
        result = supabase.table("daily_routines").insert(entry_data).execute()
        
        if result.data:
            logger.info(f"✅ Routine entry saved for user {current_user_id}")
            return result.data[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to save routine entry")
            
    except Exception as e:
        logger.error(f"❌ Error saving routine entry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save routine entry: {str(e)}")


@router.get("/entries", response_model=List[RoutineEntry])
async def get_routine_entries(
    current_user_id: str = Depends(get_current_user_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: int = 7
):
    """Get routine entries for user."""
    supabase = get_supabase()
    
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
    supabase = get_supabase()
    
    try:
        result = supabase.table("daily_routines").delete().eq(
            "id", entry_id
        ).eq("user_id", current_user_id).execute()
        
        logger.info(f"Deleted routine entry {entry_id} for user {current_user_id}")
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Error deleting routine entry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete routine entry: {str(e)}")
