"""Journal entries routes."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter()
# Prefix set in main.py: /api/v1/journal


# Schemas
class JournalEntryCreate(BaseModel):
    """Schema for creating a journal entry."""
    date: str  # ISO date format
    content: str
    mood_tag: Optional[str] = None


class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""
    content: Optional[str] = None
    mood_tag: Optional[str] = None


class JournalEntryResponse(BaseModel):
    """Schema for journal entry response."""
    id: str
    user_id: str
    date: str
    content: str
    mood_tag: Optional[str]
    created_at: str


@router.post("", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user_id: str = Depends(get_current_user_id),
):
    """Create a new journal entry."""
    supabase = get_supabase()
    
    try:
        # Validate date
        try:
            entry_date = date.fromisoformat(entry.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Create journal entry
        result = supabase.table("journal_entries").insert({
            "user_id": current_user_id,
            "date": entry_date.isoformat(),
            "content": entry.content,
            "mood_tag": entry.mood_tag,
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create journal entry")
        
        logger.info(f"Journal entry created for user {current_user_id} on {entry_date}")
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 30,
):
    """Get journal entries for the current user."""
    supabase = get_supabase()
    
    try:
        from datetime import timedelta
        since_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = (
            supabase.table("journal_entries")
            .select("*")
            .eq("user_id", current_user_id)
            .gte("date", since_date)
            .order("date", desc=True)
            .execute()
        )
        
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error fetching journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Get a specific journal entry."""
    supabase = get_supabase()
    
    try:
        result = (
            supabase.table("journal_entries")
            .select("*")
            .eq("id", entry_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry_update: JournalEntryUpdate,
    current_user_id: str = Depends(get_current_user_id),
):
    """Update a journal entry."""
    supabase = get_supabase()
    
    try:
        # Verify entry exists and belongs to user
        existing = (
            supabase.table("journal_entries")
            .select("id")
            .eq("id", entry_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Prepare update data
        update_data = {}
        if entry_update.content is not None:
            update_data["content"] = entry_update.content
        if entry_update.mood_tag is not None:
            update_data["mood_tag"] = entry_update.mood_tag
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update entry
        result = (
            supabase.table("journal_entries")
            .update(update_data)
            .eq("id", entry_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update journal entry")
        
        logger.info(f"Journal entry {entry_id} updated by user {current_user_id}")
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Delete a journal entry."""
    supabase = get_supabase()
    
    try:
        # Verify entry exists and belongs to user
        existing = (
            supabase.table("journal_entries")
            .select("id")
            .eq("id", entry_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Delete entry
        supabase.table("journal_entries").delete().eq("id", entry_id).eq("user_id", current_user_id).execute()
        
        logger.info(f"Journal entry {entry_id} deleted by user {current_user_id}")
        return {"message": "Journal entry deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))
