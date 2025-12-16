"""
Journal Insights Service
Generates daily reflective summaries using Gemini AI based on journal entries and emotion logs.
"""

import logging
from datetime import date, datetime
from typing import Dict, Optional, List, Any
import google.generativeai as genai
import json
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class JournalInsightsService:
    """Service for generating AI-powered journal insights."""
    
    def __init__(self):
        """Initialize the journal insights service."""
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
        )
        self.system_instruction = """You are a supportive, empathetic wellness companion analyzing daily journal entries. 
Your role is to:
- Provide gentle, non-judgmental reflections
- Identify emotional patterns with compassion
- Highlight positive moments and growth
- Offer one gentle suggestion for self-care (never medical advice)
- Use warm, encouraging language
- Keep summaries concise (2-3 sentences max per section)
- Never diagnose or provide medical/therapeutic advice

Response format (JSON):
{
    "summary": "Brief empathetic reflection on the day",
    "dominant_emotions": ["emotion1", "emotion2"],
    "patterns": "Observed emotional or behavioral patterns",
    "positive_signals": "Highlights of strength, resilience, or joy",
    "gentle_suggestion": "One kind suggestion for self-care or reflection"
}"""
    
    async def generate_daily_insight(
        self, 
        supabase,
        user_id: str, 
        target_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a daily insight summary for a user's journal entries and emotions.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            target_date: Date to generate insight for
            
        Returns:
            Dictionary with insight data or None if generation fails
        """
        try:
            logger.info(f"[JOURNAL][SUMMARY] Starting insight generation for user {user_id} on {target_date}")
            
            # Fetch ALL journal entries for the date
            journals = (
                supabase.table("journal_entries")
                .select("content, emotion, emotion_confidence, created_at")
                .eq("user_id", user_id)
                .eq("date", target_date.isoformat())
                .order("created_at")
                .execute()
            )
            
            if not journals.data:
                logger.warning(f"[JOURNAL][SUMMARY] No journal entries found for user {user_id} on {target_date}")
                return None
            
            logger.info(f"[JOURNAL][SUMMARY] Using {len(journals.data)} entries for {target_date}")
            
            # Fetch emotion logs for the date
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = datetime.combine(target_date, datetime.max.time())
            
            emotions = (
                supabase.table("emotion_logs")
                .select("emotion_type, confidence, trigger, source, timestamp")
                .eq("user_id", user_id)
                .gte("timestamp", start_time.isoformat())
                .lte("timestamp", end_time.isoformat())
                .order("timestamp")
                .execute()
            )
            
            logger.info(f"[JOURNAL][SUMMARY] Found {len(emotions.data) if emotions.data else 0} emotion logs for {target_date}")
            
            # Build context for Gemini - combines ALL entries
            context = self._build_context(journals.data, emotions.data if emotions.data else [])
            logger.info(f"[JOURNAL][SUMMARY] Built combined context: {len(context)} characters from {len(journals.data)} entries")
            
            # Generate insight using Gemini
            insight_data = await self._generate_with_gemini(context)
            
            if insight_data:
                logger.info(f"[JOURNAL][SUMMARY] AI successfully generated insight for {target_date}")
                # Store insight in database
                stored_insight = self._store_insight(supabase, user_id, target_date, insight_data)
                return stored_insight
            else:
                logger.error(f"[JOURNAL][SUMMARY] AI failed to generate insight for {target_date}")
            
            return None
            
        except Exception as e:
            logger.error(f"[JOURNAL][SUMMARY] Error generating daily insight: {e}")
            logger.exception(e)
            return None
    
    def _build_context(self, journals: List[Dict], emotions: List[Dict]) -> str:
        """Build context string for Gemini from journal and emotion data."""
        context_parts = []
        
        # Add journal entries
        if journals:
            context_parts.append("Journal Entries:")
            for i, journal in enumerate(journals, 1):
                content = journal.get('content', '')
                emotion = journal.get('emotion', 'unknown')
                confidence = journal.get('emotion_confidence', 0)
                context_parts.append(f"\nEntry {i} (Emotion: {emotion}, Confidence: {confidence:.2f}):")
                context_parts.append(f"{content[:500]}...")  # Limit length
        
        # Add emotion logs summary
        if emotions:
            context_parts.append("\n\nEmotion Log Summary:")
            emotion_counts = {}
            sources = set()
            for emotion_log in emotions:
                emo_type = emotion_log.get('emotion_type', 'unknown')
                source = emotion_log.get('source', 'unknown')
                emotion_counts[emo_type] = emotion_counts.get(emo_type, 0) + 1
                sources.add(source)
            
            context_parts.append(f"Emotions detected: {dict(emotion_counts)}")
            context_parts.append(f"Sources: {', '.join(sources)}")
        
        return "\n".join(context_parts)
    
    async def _generate_with_gemini(self, context: str) -> Optional[Dict[str, Any]]:
        """Generate insight using Gemini AI."""
        try:
            # Build prompt
            prompt = f"""{self.system_instruction}

Context for today:
{context}

Please provide a compassionate daily reflection in JSON format."""
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning("Empty response from Gemini")
                return None
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            insight_data = json.loads(response_text.strip())
            
            # Validate required fields
            required_fields = ['summary', 'dominant_emotions', 'patterns', 'positive_signals', 'gentle_suggestion']
            if not all(field in insight_data for field in required_fields):
                logger.warning(f"Missing required fields in Gemini response: {insight_data}")
                return None
            
            logger.info("Successfully generated insight with Gemini")
            return insight_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.debug(f"Raw response: {response.text if response else 'No response'}")
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None
    
    def _store_insight(
        self, 
        supabase, 
        user_id: str, 
        target_date: date, 
        insight_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store generated insight in database using service role."""
        try:
            # Import here to avoid circular dependency
            from app.utils.database import get_supabase
            
            # Use service role to bypass RLS when storing AI-generated insights
            service_supabase = get_supabase(use_service_role=True)
            
            # Upsert insight (update if exists, insert if not)
            # The on_conflict parameter tells Supabase which unique constraint to use
            result = (
                service_supabase.table("journal_insights")
                .upsert(
                    {
                        "user_id": user_id,
                        "date": target_date.isoformat(),
                        "summary": insight_data,
                        "updated_at": datetime.utcnow().isoformat()
                    },
                    on_conflict="user_id,date"  # Specify the unique constraint columns
                )
                .execute()
            )
            
            if result.data:
                logger.info(f"Stored insight for user {user_id} on {target_date}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error storing insight: {e}")
            raise
    
    def get_insight(self, supabase, user_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        """Retrieve existing insight for a date."""
        try:
            result = (
                supabase.table("journal_insights")
                .select("*")
                .eq("user_id", user_id)
                .eq("date", target_date.isoformat())
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving insight: {e}")
            return None


# Singleton instance
_insights_service: Optional[JournalInsightsService] = None

def get_insights_service() -> JournalInsightsService:
    """Get or create singleton insights service instance."""
    global _insights_service
    if _insights_service is None:
        _insights_service = JournalInsightsService()
    return _insights_service
