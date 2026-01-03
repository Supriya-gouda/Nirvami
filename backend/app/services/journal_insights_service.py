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
from app.services.recommendation_service import recommendation_service
from app.models.schemas import RecommendationCreate, RecommendationSource, RecommendationCategory

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
        Generate a daily insight summary with proper emotion aggregation and evidence-based analysis.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            target_date: Date to generate insight for
            
        Returns:
            Dictionary with insight data or None if generation fails
        """
        try:
            logger.info(f"[JOURNAL][REFLECTION] 🚀 Starting reflection for user {user_id} on {target_date}")
            
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
                logger.warning(f"[JOURNAL][REFLECTION] ⚠️ No journal entries found for {target_date}")
                return None
            
            logger.info(f"[JOURNAL][REFLECTION] Entries fetched: {len(journals.data)}")
            
            # PART 1: Filter valid entries (emotion exists, confidence >= 0.30)
            valid_entries = []
            for entry in journals.data:
                emotion = entry.get('emotion')
                confidence = entry.get('emotion_confidence', 0)
                
                if emotion and confidence >= 0.30:
                    valid_entries.append(entry)
                else:
                    logger.info(f"[JOURNAL][REFLECTION] Skipping entry: emotion={emotion}, confidence={confidence}")
            
            logger.info(f"[JOURNAL][REFLECTION] Valid entries after filtering: {len(valid_entries)}")
            
            if not valid_entries:
                logger.warning(f"[JOURNAL][REFLECTION] No valid entries with emotions >= 0.30")
                return None
            
            # PART 2: Compute confidence-weighted emotion scores
            emotion_scores = {}
            all_emotions = []
            
            for entry in valid_entries:
                emotion = entry['emotion']
                confidence = entry['emotion_confidence']
                
                if emotion in emotion_scores:
                    emotion_scores[emotion] += confidence
                else:
                    emotion_scores[emotion] = confidence
                
                all_emotions.append(emotion)
            
            logger.info(f"[JOURNAL][REFLECTION] Emotion scores: {emotion_scores}")
            
            # PART 3: Determine dominant emotions (exclude neutral unless clearly dominant)
            sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Check if neutral should be excluded
            dominant_emotions = []
            neutral_score = emotion_scores.get('neutral', 0)
            
            if sorted_emotions:
                top_emotion, top_score = sorted_emotions[0]
                
                # Only include neutral if it's truly dominant (25% higher than next)
                if top_emotion == 'neutral' and len(sorted_emotions) > 1:
                    second_score = sorted_emotions[1][1]
                    if top_score >= second_score * 1.25:
                        dominant_emotions = [e[0] for e in sorted_emotions[:3]]
                    else:
                        # Exclude neutral, use next emotions
                        dominant_emotions = [e[0] for e in sorted_emotions[1:4] if e[0] != 'neutral']
                else:
                    # Top emotion is not neutral, take top 2-3
                    dominant_emotions = [e[0] for e in sorted_emotions[:3] if e[0] != 'neutral']
            
            # Ensure we have at least 1 dominant emotion
            if not dominant_emotions:
                dominant_emotions = [sorted_emotions[0][0]]
            
            logger.info(f"[JOURNAL][REFLECTION] Dominant emotions selected: {dominant_emotions}")
            
            # Combine all journal content
            combined_content = "\n\n".join([e['content'] for e in valid_entries])
            
            # Generate insight with NEW evidence-based prompt
            insight_data = await self._generate_evidence_based_insight(
                combined_content,
                dominant_emotions,
                emotion_scores,
                len(valid_entries)
            )
            
            if insight_data:
                logger.info(f"[JOURNAL][REFLECTION] ✅ Generated evidence-based insight")
                logger.info(f"[JOURNAL][REFLECTION] Summary: {insight_data.get('summary', '')[:100]}...")
                logger.info(f"[JOURNAL][REFLECTION] Dominant emotions: {insight_data.get('dominant_emotions', [])}")
                logger.info(f"[JOURNAL][REFLECTION] Patterns: {insight_data.get('patterns', '')[:80]}...")
                
                # Store insight in database
                stored_insight = self._store_insight(supabase, user_id, target_date, insight_data)
                logger.info(f"[JOURNAL][DB] journal_insights upserted for {target_date}")
                
                # Extract and store recommendations
                recommendations_created = await self._extract_and_store_recommendations(
                    user_id, 
                    target_date, 
                    insight_data
                )
                
                logger.info(f"[JOURNAL][RECOMMENDATION] {len(recommendations_created)} recommendations extracted from reflection")
                for rec in recommendations_created:
                    logger.info(f"[JOURNAL][RECOMMENDATION]    - {rec.category.value}: {rec.title}")
                
                return stored_insight
            else:
                logger.error(f"[JOURNAL][REFLECTION] ❌ AI failed to generate insight")
            
            return None
            
        except Exception as e:
            logger.error(f"[JOURNAL][REFLECTION] 💥 Error: {e}")
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
    
    async def _extract_and_store_recommendations(
        self,
        user_id: str,
        target_date: date,
        insight_data: Dict[str, Any]
    ) -> List:
        """
        Extract actionable recommendations from journal insights and store them.
        
        Args:
            user_id: User ID
            target_date: Date for recommendations
            insight_data: Generated insight data with suggestions
            
        Returns:
            List of created recommendations
        """
        try:
            recommendations = []
            
            # Extract gentle_suggestion if it exists
            gentle_suggestion = insight_data.get('gentle_suggestion', '').strip()
            if gentle_suggestion:
                logger.info(f"[JOURNAL][RECS] Extracting recommendations from: '{gentle_suggestion[:100]}...'")
                
                # Use recommendation service to parse and classify
                # Build a message that includes the suggestion
                suggestion_message = f"Based on your journal reflection: {gentle_suggestion}"
                
                # Extract recommendations using the existing Gemini parser
                extracted_recs = await recommendation_service._parse_recommendations_with_gemini(suggestion_message)
                
                logger.info(f"[JOURNAL][RECS] Gemini extracted {len(extracted_recs)} recommendations from insight")
                
                # Store each recommendation
                for rec in extracted_recs:
                    try:
                        rec_create = RecommendationCreate(
                            user_id=user_id,
                            date=target_date,
                            source=RecommendationSource.JOURNAL,
                            category=RecommendationCategory(rec["category"]),
                            title=rec["title"].strip(),
                            content=rec["content"].strip(),
                            meta={
                                "extracted_from": "journal_insight",
                                "insight_date": target_date.isoformat(),
                                "original_suggestion": gentle_suggestion[:200]
                            }
                        )
                        
                        stored_rec = await recommendation_service._store_recommendation(rec_create)
                        if stored_rec:
                            recommendations.append(stored_rec)
                            logger.info(f"[JOURNAL][RECS] ✅ Stored: {stored_rec.category.value} - {stored_rec.title}")
                        else:
                            logger.warning(f"[JOURNAL][RECS] ⚠️ Failed to store (duplicate): {rec['title']}")
                            
                    except (ValueError, KeyError) as e:
                        logger.warning(f"[JOURNAL][RECS] Invalid recommendation format: {rec}. Error: {e}")
                        continue
                
                # If Gemini extraction failed, create a fallback recommendation
                if not recommendations:
                    logger.info(f"[JOURNAL][RECS] Creating fallback recommendation from gentle_suggestion")
                    try:
                        fallback_rec = RecommendationCreate(
                            user_id=user_id,
                            date=target_date,
                            source=RecommendationSource.JOURNAL,
                            category=RecommendationCategory.LIFESTYLE,
                            title="Daily Reflection Insight",
                            content=gentle_suggestion,
                            meta={
                                "extracted_from": "journal_insight_fallback",
                                "insight_date": target_date.isoformat()
                            }
                        )
                        
                        stored_rec = await recommendation_service._store_recommendation(fallback_rec)
                        if stored_rec:
                            recommendations.append(stored_rec)
                            logger.info(f"[JOURNAL][RECS] ✅ Created fallback recommendation")
                    except Exception as fallback_err:
                        logger.error(f"[JOURNAL][RECS] Failed to create fallback: {fallback_err}")
            else:
                logger.info(f"[JOURNAL][RECS] No gentle_suggestion found in insight data")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"[JOURNAL][RECS] Error extracting recommendations: {e}")
            logger.exception(e)
            return []
    
    async def _generate_evidence_based_insight(
        self, 
        combined_content: str,
        dominant_emotions: List[str],
        emotion_scores: Dict[str, float],
        num_entries: int
    ) -> Optional[Dict[str, Any]]:
        """
        Generate evidence-based insight using actual journal content and computed emotions.
        
        Args:
            combined_content: All journal entries combined
            dominant_emotions: Computed dominant emotions (excluding neutral unless justified)
            emotion_scores: Confidence-weighted scores per emotion
            num_entries: Number of journal entries
            
        Returns:
            Insight data dictionary
        """
        try:
            # Build evidence-based prompt
            prompt = f"""You are analyzing {num_entries} journal entries written today.

COMPUTED DOMINANT EMOTIONS (confidence-weighted, neutral excluded unless truly dominant):
{', '.join(dominant_emotions)}

ALL EMOTION SCORES:
{emotion_scores}

COMBINED JOURNAL CONTENT:
{combined_content[:2000]}

STRICT REQUIREMENTS:

1. SUMMARY: State the number of entries and reflect the COMPUTED dominant emotions. Be specific.
   ❌ NOT ALLOWED: "You recorded entries... emotional awareness"
   ✅ REQUIRED: "You recorded {num_entries} entries today showing recurring {dominant_emotions[0]} and {dominant_emotions[1] if len(dominant_emotions) > 1 else 'emotional intensity'}"

2. DOMINANT_EMOTIONS: Return the EXACT list provided above: {dominant_emotions}
   Do NOT add neutral unless it appears in the list.

3. PATTERNS: Analyze the ACTUAL content for:
   - Recurring emotions (same emotion multiple times)
   - Emotional intensity trends (morning heavy, evening calmer)
   - Mixed states (anxiety + anger together)
   - Transitions (high arousal → calming)
   ❌ NOT ALLOWED: "You're processing your thoughts through journaling"
   ✅ REQUIRED: "Your entries show recurring {dominant_emotions[0]} throughout the day, with emotional intensity strongest in earlier entries and slight calming toward evening"

4. POSITIVE_SIGNALS: ONLY include coping actions EXPLICITLY MENTIONED in the text:
   - breathing exercises
   - taking breaks
   - walking
   - reflection/awareness
   ❌ NOT ALLOWED: "Regular journaling is healthy"
   ✅ REQUIRED: "You used breathing and short breaks to manage stress" (only if mentioned)
   If NO coping actions mentioned: "You're maintaining awareness of your emotional state"

5. GENTLE_SUGGESTION: Must directly address the DOMINANT EMOTIONS:
   - {dominant_emotions[0]} → specific grounding/pacing techniques
   - anger → release, pause practices
   - sadness → gentle support, rest
   ❌ NOT ALLOWED: "Add more details next time"
   ✅ REQUIRED: "Since {dominant_emotions[0]} and {dominant_emotions[1] if len(dominant_emotions) > 1 else 'intensity'} appeared repeatedly, short grounding practices during the afternoon may help prevent emotional buildup"

Return ONLY valid JSON:
{{
  "summary": "...",
  "dominant_emotions": {dominant_emotions},
  "patterns": "...",
  "positive_signals": "...",
  "gentle_suggestion": "..."
}}"""
            
            logger.info(f"[JOURNAL][REFLECTION] Generating evidence-based insight...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning("[JOURNAL][REFLECTION] Empty response from Gemini")
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
                logger.warning(f"[JOURNAL][REFLECTION] Missing required fields: {insight_data}")
                return None
            
            # Log pattern detection
            logger.info(f"[JOURNAL][REFLECTION] Patterns detected: {insight_data['patterns'][:100]}...")
            logger.info(f"[JOURNAL][REFLECTION] Positive signals: {insight_data['positive_signals'][:100]}...")
            logger.info(f"[JOURNAL][REFLECTION] Suggestions generated based on {', '.join(dominant_emotions)} dominance")
            
            logger.info("[JOURNAL][REFLECTION] Successfully generated evidence-based insight")
            return insight_data
            
        except json.JSONDecodeError as e:
            logger.error(f"[JOURNAL][REFLECTION] Failed to parse Gemini JSON: {e}")
            logger.debug(f"Raw response: {response.text if response else 'No response'}")
            return None
        except Exception as e:
            logger.error(f"[JOURNAL][REFLECTION] Error calling Gemini: {e}")
            return None
    
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
        """Store generated insight in database using service role (upsert by user_id + date)."""
        try:
            # Import here to avoid circular dependency
            from app.utils.database import get_supabase
            
            logger.info(f"[JOURNAL][DB] 💾 Upserting insight to journal_insights table...")
            logger.info(f"[JOURNAL][DB]    - user_id: {user_id}")
            logger.info(f"[JOURNAL][DB]    - date: {target_date.isoformat()}")
            logger.info(f"[JOURNAL][DB]    - on_conflict: user_id,date (will update if exists)")
            
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
                insight_id = result.data[0].get('id', 'N/A')
                created_at = result.data[0].get('created_at', 'N/A')
                updated_at = result.data[0].get('updated_at', 'N/A')
                logger.info(f"[JOURNAL][DB] ✅ Successfully upserted insight:")
                logger.info(f"[JOURNAL][DB]    - ID: {insight_id}")
                logger.info(f"[JOURNAL][DB]    - Created: {created_at}")
                logger.info(f"[JOURNAL][DB]    - Updated: {updated_at}")
                return result.data[0]
            
            logger.warning(f"[JOURNAL][DB] ⚠️ Upsert returned no data")
            return None
            
        except Exception as e:
            logger.error(f"[JOURNAL][DB] ❌ Error storing insight: {e}")
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
