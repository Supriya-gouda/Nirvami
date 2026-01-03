"""Journal entries routes."""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.services.emotion_service import get_emotion_service
from app.services.journal_insights_service import get_insights_service
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()
# Prefix set in main.py: /api/v1/journal


# Schemas
class JournalEntryCreate(BaseModel):
    """Schema for creating a journal entry."""
    content: str = Field(..., min_length=1, max_length=2000, description="Journal entry content (max 2000 chars)")
    date: Optional[str] = None  # ISO date format, defaults to today


class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""
    content: str = Field(..., min_length=1, max_length=2000, description="Updated journal content")


class JournalEntryResponse(BaseModel):
    """Schema for journal entry response."""
    id: str
    user_id: str
    date: str
    content: str
    emotion: Optional[str] = None
    emotion_confidence: Optional[float] = None
    created_at: str


class JournalSummarizeRequest(BaseModel):
    """Schema for requesting journal summarization."""
    date: str = Field(..., description="Date to summarize in YYYY-MM-DD format")
    regenerate: bool = Field(default=False, description="Force regenerate even if cached")


class JournalInsightResponse(BaseModel):
    """Schema for journal insight response."""
    id: str
    user_id: str
    date: str
    summary: Dict[str, Any]  # Contains: summary, dominant_emotions, patterns, positive_signals, gentle_suggestion
    created_at: str
    updated_at: str


@router.post("", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    request: Request,
    current_user_id: str = Depends(get_current_user_id),
):
    """Create a new journal entry with emotion detection."""
    # Use service role to bypass RLS for backend operations
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Validate content length
        if len(entry.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="Journal content cannot be empty")
        
        if len(entry.content) > 2000:
            raise HTTPException(status_code=400, detail="Journal content exceeds 2000 character limit")
        
        # Determine entry date
        if entry.date:
            try:
                entry_date = date.fromisoformat(entry.date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            entry_date = date.today()
        
        # Generate unique ID
        journal_id = str(uuid.uuid4())
        logger.info(f"[JOURNAL] Creating journal entry {journal_id} for user {current_user_id} on {entry_date}")
        logger.info(f"[JOURNAL] Content length: {len(entry.content)} chars")
        
        # STEP 1: Detect emotion using the SAME service as Chat with journal-specific threshold
        emotion_type = None
        emotion_confidence = None
        
        try:
            # Get model_manager from app state (loaded during startup)
            model_manager = getattr(request.app.state, 'model_manager', None)
            emotion_service = get_emotion_service(model_manager)
            
            logger.info(f"[JOURNAL][EMOTION] Running ML emotion detection on journal text")
            logger.info(f"[JOURNAL][EMOTION] Text length: {len(entry.content)} chars")
            
            # Use the SAME detect_emotion function as Chat with source="journal" for lower threshold (0.40)
            emotion_result = emotion_service.detect_emotion(entry.content, source="journal")
            
            emotion_type = emotion_result.get('primary_emotion')
            emotion_confidence = emotion_result.get('confidence')
            detection_source = emotion_result.get('source', 'unknown')
            
            logger.info(f"[JOURNAL][EMOTION] Detected: {emotion_type} (confidence: {emotion_confidence:.2f})")
            logger.info(f"[JOURNAL][EMOTION] Source: {detection_source}")
            
            if detection_source == 'rules' and emotion_type == 'neutral':
                logger.warning(f"[JOURNAL][EMOTION] Fell back to rules and got neutral - ML may have failed or threshold too high")
            
        except Exception as ml_err:
            logger.error(f"[JOURNAL][EMOTION] ML detection failed: {ml_err}")
            logger.exception(ml_err)
            # Leave as NULL if ML fails - do NOT default to neutral
        
        # STEP 2: Save journal entry with emotion data
        logger.info(f"[JOURNAL][DB] Saving entry to database")
        logger.info(f"[JOURNAL][DB] journal_id={journal_id}, user_id={current_user_id}")
        logger.info(f"[JOURNAL][DB] date={entry_date.isoformat()}, emotion={emotion_type}, confidence={emotion_confidence}")
        
        result = supabase.table("journal_entries").insert({
            "id": journal_id,
            "user_id": current_user_id,
            "date": entry_date.isoformat(),
            "content": entry.content,
            "emotion": emotion_type,
            "emotion_confidence": emotion_confidence,
        }).execute()
        
        if not result.data:
            logger.error(f"[JOURNAL][DB] Failed to create journal entry - no data returned from database")
            raise HTTPException(status_code=500, detail="Failed to create journal entry")
        
        saved_entry = result.data[0]
        logger.info(f"[JOURNAL][DB] ✅ Journal entry saved successfully:")
        logger.info(f"[JOURNAL][DB]    - ID: {saved_entry.get('id')}")
        logger.info(f"[JOURNAL][DB]    - Date: {saved_entry.get('date')}")
        logger.info(f"[JOURNAL][DB]    - Emotion: {saved_entry.get('emotion')} ({saved_entry.get('emotion_confidence')})")
        logger.info(f"[JOURNAL][DB]    - Created at: {saved_entry.get('created_at')}")
        
        # Verify emotion was persisted
        if emotion_type and saved_entry.get('emotion') != emotion_type:
            logger.error(f"[JOURNAL][DB] CRITICAL: Emotion mismatch! Expected {emotion_type}, got {saved_entry.get('emotion')}")
            raise HTTPException(status_code=500, detail="Failed to persist emotion data")
        
        return saved_entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[JOURNAL] Error creating journal entry: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    date_filter: Optional[str] = None,
    days: int = 30,
    current_user_id: str = Depends(get_current_user_id),
):
    """
    Get journal entries for the current user.
    
    Args:
        date_filter: Optional date filter in YYYY-MM-DD format (returns entries for that specific date)
        days: Number of days to fetch if date_filter not specified (default 30)
    """
    # Use service role to bypass RLS
    supabase = get_supabase(use_service_role=True)
    
    try:
        logger.info(f"[JOURNAL][GET] Fetching entries for user {current_user_id}, date_filter={date_filter}, days={days}")
        
        # If specific date provided, filter by exact date
        if date_filter:
            try:
                target_date = date_filter if isinstance(date_filter, str) else date_filter
                logger.info(f"[JOURNAL][GET] Filtering by specific date: {target_date}")
                result = (
                    supabase.table("journal_entries")
                    .select("*")
                    .eq("user_id", current_user_id)
                    .eq("date", target_date)
                    .order("created_at", desc=True)
                    .execute()
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            # Fetch last N days
            from datetime import timedelta
            since_date = (date.today() - timedelta(days=days)).isoformat()
            logger.info(f"[JOURNAL][GET] Fetching entries since {since_date} (last {days} days)")
            result = (
                supabase.table("journal_entries")
                .select("*")
                .eq("user_id", current_user_id)
                .gte("date", since_date)
                .order("created_at", desc=True)
                .execute()
            )
        
        entries_count = len(result.data) if result.data else 0
        logger.info(f"[JOURNAL][GET] Returning {entries_count} entries for user {current_user_id}")
        
        if entries_count > 0:
            dates = list(set([e.get('date') for e in result.data]))
            logger.info(f"[JOURNAL][GET] Dates in response: {sorted(dates)}")
        
        return result.data if result.data else []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[JOURNAL][GET] Error fetching journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Get a specific journal entry."""
    # Use service role to bypass RLS
    supabase = get_supabase(use_service_role=True)
    
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
    request: Request,
    current_user_id: str = Depends(get_current_user_id),
):
    """Update a journal entry and re-run emotion detection."""
    # Use service role to bypass RLS
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Validate content length
        if len(entry_update.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="Journal content cannot be empty")
        
        if len(entry_update.content) > 2000:
            raise HTTPException(status_code=400, detail="Journal content exceeds 2000 character limit")
        
        # Verify entry exists and belongs to user
        existing = (
            supabase.table("journal_entries")
            .select("id, date")
            .eq("id", entry_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Check if entry is from today (only allow same-day edits)
        entry_date = date.fromisoformat(existing.data[0]['date'])
        if entry_date != date.today():
            raise HTTPException(status_code=403, detail="Can only edit today's journal entries")
        
        logger.info(f"[JOURNAL] Updating journal entry {entry_id} for user {current_user_id}")
        logger.info(f"[JOURNAL] New content length: {len(entry_update.content)} chars")
        
        # Re-run emotion detection using the SAME service as Chat with journal-specific threshold
        emotion_type = None
        emotion_confidence = None
        
        try:
            # Get model_manager from app state (loaded during startup)
            model_manager = getattr(request.app.state, 'model_manager', None)
            emotion_service = get_emotion_service(model_manager)
            
            logger.info(f"[JOURNAL][EMOTION] Running ML emotion detection on updated text")
            logger.info(f"[JOURNAL][EMOTION] Text length: {len(entry_update.content)} chars")
            
            # Use the SAME detect_emotion function as Chat with source="journal" for lower threshold (0.40)
            emotion_result = emotion_service.detect_emotion(entry_update.content, source="journal")
            
            emotion_type = emotion_result.get('primary_emotion')
            emotion_confidence = emotion_result.get('confidence')
            detection_source = emotion_result.get('source', 'unknown')
            
            logger.info(f"[JOURNAL][EMOTION] Detected: {emotion_type} (confidence: {emotion_confidence:.2f})")
            logger.info(f"[JOURNAL][EMOTION] Source: {detection_source}")
            
            if detection_source == 'rules' and emotion_type == 'neutral':
                logger.warning(f"[JOURNAL][EMOTION] Fell back to rules and got neutral - ML may have failed or threshold too high")
            
        except Exception as ml_err:
            logger.error(f"[JOURNAL][EMOTION] ML detection failed: {ml_err}")
            logger.exception(ml_err)
            # Leave as NULL if ML fails
        
        # Update entry
        update_data = {
            "content": entry_update.content,
            "emotion": emotion_type,
            "emotion_confidence": emotion_confidence,
        }
        
        logger.info(f"[JOURNAL][DB] Updating journal entry {entry_id}")
        logger.info(f"[JOURNAL][DB] emotion={emotion_type}, confidence={emotion_confidence}")
        
        result = (
            supabase.table("journal_entries")
            .update(update_data)
            .eq("id", entry_id)
            .eq("user_id", current_user_id)
            .execute()
        )
        
        if not result.data:
            logger.error(f"[JOURNAL][DB] Failed to update journal entry")
            raise HTTPException(status_code=500, detail="Failed to update journal entry")
        
        updated_entry = result.data[0]
        logger.info(f"[JOURNAL][DB] Journal entry {entry_id} updated successfully")
        logger.info(f"[JOURNAL][DB] Returned emotion: {updated_entry.get('emotion')}, confidence: {updated_entry.get('emotion_confidence')}")
        
        # Verify emotion was persisted
        if emotion_type and updated_entry.get('emotion') != emotion_type:
            logger.error(f"[JOURNAL][DB] CRITICAL: Emotion mismatch! Expected {emotion_type}, got {updated_entry.get('emotion')}")
            raise HTTPException(status_code=500, detail="Failed to persist emotion data")
        
        return updated_entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[JOURNAL] Error updating journal entry: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Delete a journal entry."""
    # Use service role to bypass RLS
    supabase = get_supabase(use_service_role=True)
    
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


@router.post("/summarize", response_model=JournalInsightResponse)
async def generate_journal_summary(
    request: JournalSummarizeRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    """
    Generate a daily reflective summary using Gemini AI.
    Analyzes journal entries and emotion logs for the specified date.
    REQUIRES at least one journal entry to exist for the date.
    """
    # Use service role to bypass RLS
    supabase = get_supabase(use_service_role=True)
    insights_service = get_insights_service()
    
    try:
        # Parse date with proper timezone handling (normalize to UTC midnight)
        target_date = date.fromisoformat(request.date)
        logger.info(f"📊 [SUMMARIZE] Starting insight generation for user {current_user_id} on {target_date}")
        
        # Check if insight already exists
        existing_insight = insights_service.get_insight(supabase, current_user_id, target_date)
        if existing_insight and not request.regenerate:
            logger.info(f"✅ [SUMMARIZE] Returning cached insight for user {current_user_id} on {target_date}")
            return existing_insight
        
        # Fetch journal entries for the date
        logger.info(f"🔍 [SUMMARIZE] Fetching journal entries for {target_date}")
        journals = (
            supabase.table("journal_entries")
            .select("*")
            .eq("user_id", current_user_id)
            .eq("date", target_date.isoformat())
            .execute()
        )
        
        logger.info(f"📝 [SUMMARIZE] Found {len(journals.data) if journals.data else 0} journal entries for {target_date}")
        
        # CRITICAL: If no entries exist, return error - user must save journal first
        if not journals.data or len(journals.data) == 0:
            logger.warning(f"⚠️ [SUMMARIZE] No journal entries found for {target_date} - user must save first")
            raise HTTPException(
                status_code=400, 
                detail="No journal entries found for this date. Please save your journal entry first before generating insights."
            )
        
        # Generate insight with AI
        logger.info(f"🤖 [SUMMARIZE] Generating AI insight with {len(journals.data)} entries")
        insight = await insights_service.generate_daily_insight(
            supabase, 
            current_user_id, 
            target_date
        )
        
        if not insight:
            # If AI generation fails, create a meaningful fallback based on actual journal content
            logger.warning(f"⚠️ [SUMMARIZE] AI insight generation failed, creating fallback with journal data")
            
            # Extract emotions from journal entries
            emotions_detected = [j.get('emotion') for j in journals.data if j.get('emotion')]
            unique_emotions = list(set(emotions_detected)) if emotions_detected else ['neutral']
            
            fallback_summary = {
                "summary": f"You recorded {len(journals.data)} journal {'entry' if len(journals.data) == 1 else 'entries'} today. Your reflections show emotional awareness.",
                "dominant_emotions": unique_emotions,
                "patterns": "You're taking time to process your thoughts and feelings through journaling",
                "positive_signals": "Regular journaling is a healthy practice for emotional wellbeing",
                "gentle_suggestion": "Consider adding more details about your experiences to gain deeper insights"
            }
            insight = insights_service._store_insight(
                supabase, 
                current_user_id, 
                target_date, 
                fallback_summary
            )
        
        logger.info(f"✅ [SUMMARIZE] Successfully generated insight for user {current_user_id} on {target_date}")
        return insight
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error generating journal summary: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating insights")

