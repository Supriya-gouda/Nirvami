"""
Recommendation Service
Extracts and stores yoga, Ayurveda, and lifestyle recommendations from AI chat and device analysis
"""
import logging
import json
import hashlib
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Union
from uuid import UUID

from app.models.schemas import (
    RecommendationCreate, 
    Recommendation, 
    RecommendationSource, 
    RecommendationCategory,
    DailyRecommendationsResponse
)
from app.utils.database import get_supabase
from app.services.gemini_chatbot import GeminiChatbot
from app.ml.model_manager import ModelManager

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for extracting, storing, and retrieving recommendations"""
    
    def __init__(self):
        """Initialize with Gemini chatbot for parsing"""
        self.gemini = GeminiChatbot()
        self.model_manager = ModelManager()
    
    def _safe_parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Safely parse timestamp strings from Supabase, handling microsecond precision issues
        
        Args:
            timestamp_str: ISO format timestamp string
            
        Returns:
            datetime object
        """
        try:
            # Handle various timestamp formats from Supabase
            if '+' in timestamp_str and timestamp_str.count('.') == 1:
                # Remove microseconds precision beyond 6 digits if present
                if '.' in timestamp_str:
                    main_part, micro_tz_part = timestamp_str.split('.')
                    if '+' in micro_tz_part:
                        micro_part, tz_part = micro_tz_part.split('+')
                        micro_part = micro_part[:6].ljust(6, '0')  # Ensure exactly 6 digits
                        timestamp_str = f"{main_part}.{micro_part}+{tz_part}"
                    elif '-' in micro_tz_part:
                        micro_part, tz_part = micro_tz_part.split('-')
                        micro_part = micro_part[:6].ljust(6, '0')  # Ensure exactly 6 digits
                        timestamp_str = f"{main_part}.{micro_part}-{tz_part}"
            
            return datetime.fromisoformat(timestamp_str)
        except ValueError as e:
            logger.warning(f"Timestamp parsing error for '{timestamp_str}': {e}")
            # Fallback to current time
            return datetime.now()
    
    async def extract_and_store_recommendations_from_chat(
        self, 
        user_id: str, 
        message_text: str, 
        timestamp: datetime,
        timezone_offset: Optional[int] = None
    ) -> List[Recommendation]:
        """
        Extract yoga & Ayurveda recommendations from chat assistant response using Gemini
        
        Args:
            user_id: User ID
            message_text: Assistant's response text to parse
            timestamp: When the message was created
            timezone_offset: User's timezone offset in minutes (optional)
        
        Returns:
            List of stored recommendations
        """
        try:
            logger.info(f"[REC_EXTRACT] Starting extraction for user {user_id}, message length: {len(message_text)}")
            
            # Calculate the date based on timestamp and timezone
            user_date = self._get_user_date(timestamp, timezone_offset)
            logger.info(f"[REC_EXTRACT] Target date: {user_date}")
            
            # Parse recommendations using Gemini
            extracted_recs = await self._parse_recommendations_with_gemini(message_text)
            
            if not extracted_recs:
                logger.info(f"No recommendations extracted from chat for user {user_id}")
                return []
            
            # Convert to RecommendationCreate objects and store
            recommendations = []
            for rec in extracted_recs:
                try:
                    rec_create = RecommendationCreate(
                        user_id=user_id,
                        date=user_date,
                        source=RecommendationSource.CHAT,
                        category=RecommendationCategory(rec["category"]),
                        title=rec["title"].strip(),
                        content=rec["content"].strip(),
                        meta={"extracted_from": "chat", "original_timestamp": timestamp.isoformat()}
                    )
                    
                    stored_rec = await self._store_recommendation(rec_create)
                    if stored_rec:
                        recommendations.append(stored_rec)
                        logger.info(f"[REC_EXTRACT] Stored recommendation: {stored_rec.category} - {stored_rec.title}")
                    else:
                        logger.warning(f"[REC_EXTRACT] Failed to store recommendation (possible duplicate): {rec['title']}")
                        
                except (ValueError, KeyError) as e:
                    logger.warning(f"[REC_EXTRACT] Invalid recommendation format, skipping: {rec}. Error: {e}")
                    continue
            
            logger.info(f"[REC_EXTRACT] ✅ Stored {len(recommendations)} recommendations from chat for user {user_id} on {user_date}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error extracting recommendations from chat: {e}", exc_info=True)
            return []
    
    async def save_device_recommendations(
        self, 
        user_id: str, 
        target_date: date, 
        device_recs: List[str]
    ) -> List[Recommendation]:
        """
        Save device-generated recommendations to recommendations table
        
        Args:
            user_id: User ID
            target_date: Date for the recommendations
            device_recs: List of recommendation strings from device analysis
        
        Returns:
            List of stored recommendations
        """
        try:
            if not device_recs:
                return []
            
            recommendations = []
            for rec_text in device_recs:
                try:
                    # Classify the recommendation
                    category, title = self._classify_device_recommendation(rec_text)
                    
                    rec_create = RecommendationCreate(
                        user_id=user_id,
                        date=target_date,
                        source=RecommendationSource.DEVICE,
                        category=category,
                        title=title,
                        content=rec_text.strip(),
                        meta={"extracted_from": "device_analysis"}
                    )
                    
                    stored_rec = await self._store_recommendation(rec_create)
                    if stored_rec:
                        recommendations.append(stored_rec)
                        
                except Exception as e:
                    logger.warning(f"Error storing device recommendation '{rec_text}': {e}")
                    continue
            
            logger.info(f"Stored {len(recommendations)} device recommendations for user {user_id} on {target_date}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error saving device recommendations: {e}", exc_info=True)
            return []
    
    async def get_daily_recommendations(
        self, 
        user_id: str, 
        target_date: Optional[date] = None
    ) -> DailyRecommendationsResponse:
        """
        Get all recommendations for a specific date, grouped by category
        
        Args:
            user_id: User ID
            target_date: Date to get recommendations for (defaults to today)
        
        Returns:
            DailyRecommendationsResponse with recommendations grouped by category
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            logger.info(f"[GET_DAILY] Fetching recommendations for user {user_id} on {target_date}")
            
            supabase = get_supabase()
            
            # Fetch recommendations for the date
            result = supabase.table("recommendations")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("date", target_date.isoformat())\
                .order("created_at", desc=True)\
                .execute()
            
            logger.info(f"[GET_DAILY] Found {len(result.data or [])} total recommendations for {target_date}")
            
            if not result.data:
                logger.info(f"[GET_DAILY] No recommendations found for user {user_id} on {target_date}")
                return DailyRecommendationsResponse(date=target_date)
            
            # Group by category
            grouped_recs = {
                "yoga": [],
                "ayurveda": [],
                "lifestyle": [],
                "sleep": [],
                "breathing": [],
                "meditation": [],
                "diet": []
            }
            
            for rec_data in result.data:
                try:
                    # Parse the date more safely
                    rec_date = rec_data["date"]
                    if isinstance(rec_date, str):
                        parsed_date = datetime.fromisoformat(rec_date).date()
                    else:
                        parsed_date = rec_date
                    
                    rec = Recommendation(
                        id=rec_data["id"],
                        user_id=rec_data["user_id"],
                        date=parsed_date,
                        source=RecommendationSource(rec_data["source"]),
                        category=RecommendationCategory(rec_data["category"]),
                        title=rec_data["title"],
                        content=rec_data["content"],
                        created_at=self._safe_parse_timestamp(rec_data["created_at"]),
                        meta=rec_data.get("meta", {})
                    )
                    
                    category = rec.category.value
                    if category in grouped_recs:
                        grouped_recs[category].append(rec)
                        logger.debug(f"[GET_DAILY] Added {category} recommendation: {rec.title}")
                    else:
                        logger.warning(f"[GET_DAILY] Unknown category: {category}")
                        
                except Exception as rec_error:
                    logger.error(f"[GET_DAILY] Error processing recommendation {rec_data.get('id')}: {rec_error}")
                    continue
            
            # Log summary
            total_by_category = {cat: len(recs) for cat, recs in grouped_recs.items() if recs}
            logger.info(f"[GET_DAILY] Grouped recommendations: {total_by_category}")
            
            return DailyRecommendationsResponse(
                date=target_date,
                yoga=grouped_recs["yoga"],
                ayurveda=grouped_recs["ayurveda"],
                lifestyle=grouped_recs["lifestyle"],
                sleep=grouped_recs["sleep"],
                breathing=grouped_recs["breathing"],
                meditation=grouped_recs["meditation"],
                diet=grouped_recs["diet"]
            )
            
        except Exception as e:
            logger.error(f"Error fetching daily recommendations: {e}", exc_info=True)
            return DailyRecommendationsResponse(date=target_date or date.today())
    
    async def get_recommendations_by_category(
        self, 
        user_id: str, 
        category: Union[RecommendationCategory, str],
        target_date: Optional[date] = None
    ) -> List[Recommendation]:
        """
        Get recommendations for a specific category and date
        
        Args:
            user_id: User ID  
            category: Recommendation category (enum or string)
            target_date: Date to get recommendations for (defaults to today)
        
        Returns:
            List of recommendations for the category
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            # Handle both enum and string category inputs
            category_str = category.value if hasattr(category, 'value') else str(category)
            
            logger.info(f"[GET_CATEGORY] Fetching {category_str} recommendations for user {user_id} on {target_date}")
            
            supabase = get_supabase()
            
            result = supabase.table("recommendations")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("date", target_date.isoformat())\
                .eq("category", category_str)\
                .order("created_at", desc=True)\
                .execute()
            
            logger.info(f"[GET_CATEGORY] Found {len(result.data or [])} {category_str} recommendations")
            
            recommendations = []
            for rec_data in result.data:
                rec = Recommendation(
                    id=rec_data["id"],
                    user_id=rec_data["user_id"],
                    date=datetime.fromisoformat(rec_data["date"]).date(),
                    source=RecommendationSource(rec_data["source"]),
                    category=RecommendationCategory(rec_data["category"]),
                    title=rec_data["title"],
                    content=rec_data["content"],
                    created_at=self._safe_parse_timestamp(rec_data["created_at"]),
                    meta=rec_data.get("meta", {})
                )
                recommendations.append(rec)
            
            logger.info(f"Found {len(recommendations)} {category_str} recommendations for user {user_id} on {target_date}")
            return recommendations
            
        except Exception as e:
            category_str = category.value if hasattr(category, 'value') else str(category)
            logger.error(f"Error fetching {category_str} recommendations: {e}", exc_info=True)
            return []
    
    # Private helper methods
    
    async def _parse_recommendations_with_gemini(self, message_text: str) -> List[Dict[str, str]]:
        """
        Use Gemini to parse recommendations from assistant response
        
        Args:
            message_text: Assistant's response text to parse
        
        Returns:
            List of recommendation dictionaries with category, title, content
        """
        if not self.gemini or not self.gemini.model:
            logger.warning("[REC_EXTRACT] Gemini not available for recommendation parsing")
            return []
        
        try:
            logger.info(f"[REC_EXTRACT] Using Gemini to parse message length: {len(message_text)}")
            
            # Create extraction prompt
            extraction_prompt = f"""You are an expert AI recommendation parser. Analyze the following assistant response and extract ONLY actionable yoga, Ayurveda, and lifestyle recommendations.

IMPORTANT RULES:
1. Only extract specific, actionable recommendations (not general explanations)
2. Each recommendation should be something the user can actually DO
3. Be specific about yoga poses, breathing techniques, lifestyle changes, diet suggestions, etc.
4. If no actionable recommendations exist, return an empty array []

CATEGORIES:
- "yoga": Specific yoga poses, movements, stretches, physical practices
- "ayurveda": Ayurvedic practices, doshas, traditional remedies, herbs
- "lifestyle": Daily routine changes, habits, environment adjustments  
- "sleep": Sleep-related practices, bedtime routines, sleep hygiene
- "breathing": Pranayama, breathing exercises, breathwork
- "meditation": Meditation techniques, mindfulness practices
- "diet": Specific food recommendations, eating habits, nutrition

Return ONLY valid JSON in this exact format:

[
  {{
    "category": "yoga|ayurveda|lifestyle|sleep|breathing|meditation|diet",
    "title": "Brief descriptive title (max 50 chars)",
    "content": "Detailed actionable recommendation with specific steps"
  }}
]

Assistant response to analyze:
{message_text}"""
            
            # Generate response from Gemini
            logger.info(f"[REC_EXTRACT] Sending extraction prompt to Gemini...")
            response = self.gemini.model.generate_content(extraction_prompt)
            
            if not response or not response.text:
                logger.warning("[REC_EXTRACT] No response from Gemini for recommendation extraction")
                return []
            
            logger.info(f"[REC_EXTRACT] Gemini response length: {len(response.text)}")
            logger.info(f"[REC_EXTRACT] Gemini raw response: {response.text[:500]}...")
            
            # Clean the response - remove code blocks if present
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]   # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove trailing ```
            
            response_text = response_text.strip()
            logger.info(f"[REC_EXTRACT] Cleaned response for JSON parsing: {response_text[:200]}...")
            
            # Try to parse JSON response
            try:
                logger.info(f"[REC_EXTRACT] Attempting to parse JSON response...")
                extracted_recs = json.loads(response_text)
                
                if not isinstance(extracted_recs, list):
                    logger.warning(f"[REC_EXTRACT] Gemini response is not a list, got: {type(extracted_recs)}")
                    return []
                
                logger.info(f"[REC_EXTRACT] Parsed {len(extracted_recs)} raw recommendations")
                
                # Validate each recommendation
                valid_recs = []
                for i, rec in enumerate(extracted_recs):
                    if (isinstance(rec, dict) and 
                        "category" in rec and 
                        "title" in rec and 
                        "content" in rec):
                        valid_recs.append(rec)
                        logger.info(f"[REC_EXTRACT] Valid rec {i+1}: {rec['category']} - {rec['title'][:50]}...")
                    else:
                        logger.warning(f"[REC_EXTRACT] Invalid rec {i+1}: missing required fields")
                
                logger.info(f"[REC_EXTRACT] Extracted {len(valid_recs)} valid recommendations using Gemini")
                return valid_recs
                
            except json.JSONDecodeError as e:
                logger.warning(f"[REC_EXTRACT] Failed to parse Gemini response as JSON: {e}")
                logger.warning(f"[REC_EXTRACT] Cleaned response that failed: {response_text}")
                return []
            
        except Exception as e:
            logger.error(f"[REC_EXTRACT] Error parsing recommendations with Gemini: {e}", exc_info=True)
            
            # Fallback: Try basic keyword extraction
            logger.info("[REC_EXTRACT] Attempting fallback keyword extraction...")
            return self._fallback_extract_recommendations(message_text)
    
    def _fallback_extract_recommendations(self, message_text: str) -> List[Dict[str, str]]:
        """
        Fallback method to extract recommendations using keyword matching
        """
        recommendations = []
        text_lower = message_text.lower()
        
        # Look for yoga-related content
        if any(keyword in text_lower for keyword in ['pose', 'asana', 'stretch', 'yoga', 'exercise', 'movement']):
            if 'try' in text_lower or 'practice' in text_lower or 'do' in text_lower:
                recommendations.append({
                    "category": "yoga",
                    "title": "Yoga Practice Suggestion",
                    "content": message_text[:500] + "..." if len(message_text) > 500 else message_text
                })
        
        # Look for breathing-related content
        if any(keyword in text_lower for keyword in ['breath', 'pranayama', 'inhale', 'exhale', 'breathing']):
            if 'try' in text_lower or 'practice' in text_lower:
                recommendations.append({
                    "category": "breathing",
                    "title": "Breathing Exercise",
                    "content": message_text[:500] + "..." if len(message_text) > 500 else message_text
                })
        
        # Look for lifestyle/ayurveda content
        if any(keyword in text_lower for keyword in ['daily', 'routine', 'lifestyle', 'ayurveda', 'dosha', 'balance']):
            if 'try' in text_lower or 'consider' in text_lower or 'practice' in text_lower:
                recommendations.append({
                    "category": "ayurveda",
                    "title": "Ayurvedic Guidance",
                    "content": message_text[:500] + "..." if len(message_text) > 500 else message_text
                })
        
        logger.info(f"[REC_EXTRACT] Fallback extraction found {len(recommendations)} recommendations")
        return recommendations
    
    def _classify_device_recommendation(self, rec_text: str) -> tuple[RecommendationCategory, str]:
        """
        Classify device recommendation into category and generate title
        
        Args:
            rec_text: Recommendation text from device analysis
        
        Returns:
            Tuple of (category, title)
        """
        rec_lower = rec_text.lower()
        
        # Yoga/stretching/movement keywords
        if any(keyword in rec_lower for keyword in [
            "yoga", "stretch", "asana", "pose", "movement", "exercise", 
            "flexible", "mobility", "relaxation", "tension"
        ]):
            return RecommendationCategory.YOGA, "Movement Practice"
        
        # Sleep keywords  
        elif any(keyword in rec_lower for keyword in [
            "sleep", "rest", "bed", "nap", "tired", "exhaustion", 
            "recovery", "restorative"
        ]):
            return RecommendationCategory.SLEEP, "Sleep & Recovery"
        
        # Breathing keywords
        elif any(keyword in rec_lower for keyword in [
            "breath", "breathing", "pranayama", "oxygen", "deep breath"
        ]):
            return RecommendationCategory.BREATHING, "Breathing Practice"
        
        # Meditation keywords
        elif any(keyword in rec_lower for keyword in [
            "meditat", "mindful", "awareness", "focus", "calm", "peace"
        ]):
            return RecommendationCategory.MEDITATION, "Mindfulness Practice"
        
        # Diet/nutrition keywords
        elif any(keyword in rec_lower for keyword in [
            "eat", "food", "diet", "nutrition", "meal", "drink", "water",
            "spice", "herb", "tea", "warm", "cold"
        ]):
            return RecommendationCategory.DIET, "Nutrition Guidance"
        
        # Ayurveda-specific keywords
        elif any(keyword in rec_lower for keyword in [
            "dosha", "vata", "pitta", "kapha", "ayurveda", "daily routine",
            "dinacharya", "oil", "massage", "warm", "routine"
        ]):
            return RecommendationCategory.AYURVEDA, "Ayurvedic Practice"
        
        # Default to lifestyle
        else:
            return RecommendationCategory.LIFESTYLE, "Lifestyle Adjustment"
    
    async def _store_recommendation(self, rec_create: RecommendationCreate) -> Optional[Recommendation]:
        """
        Store a single recommendation with deduplication
        
        Args:
            rec_create: Recommendation to store
        
        Returns:
            Stored recommendation or None if duplicate/error
        """
        try:
            supabase = get_supabase(use_service_role=True)
            
            # Prepare data for insertion
            rec_data = {
                "user_id": rec_create.user_id,
                "date": rec_create.date.isoformat(),
                "source": rec_create.source.value,
                "category": rec_create.category.value,
                "title": rec_create.title,
                "content": rec_create.content,
                "meta": rec_create.meta
            }
            
            logger.info(f"[REC_STORE] Attempting to store: {rec_create.category.value} - {rec_create.title[:50]}")
            
            # Insert with conflict resolution (will be handled by unique constraint)
            result = supabase.table("recommendations")\
                .insert(rec_data)\
                .execute()
            
            if result.data:
                rec_data = result.data[0]
                logger.info(f"[REC_STORE] ✅ Successfully stored recommendation with ID: {rec_data['id']}")
                return Recommendation(
                    id=rec_data["id"],
                    user_id=rec_data["user_id"],
                    date=datetime.fromisoformat(rec_data["date"]).date(),
                    source=RecommendationSource(rec_data["source"]),
                    category=RecommendationCategory(rec_data["category"]),
                    title=rec_data["title"],
                    content=rec_data["content"],
                    created_at=datetime.fromisoformat(rec_data["created_at"]),
                    meta=rec_data.get("meta", {})
                )
            
            logger.warning(f"[REC_STORE] No data returned from insert operation")
            return None
            
        except Exception as e:
            # Check if it's a duplicate (unique constraint violation)
            error_msg = str(e).lower()
            if "duplicate" in error_msg or "unique" in error_msg or "constraint" in error_msg:
                logger.info(f"[REC_STORE] Duplicate recommendation skipped for user {rec_create.user_id}: {rec_create.title}")
                return None
            
            logger.error(f"[REC_STORE] Error storing recommendation: {e}", exc_info=True)
            return None
    
    def _get_user_date(self, timestamp: datetime, timezone_offset: Optional[int] = None) -> date:
        """
        Get the user's local date based on timestamp and timezone offset
        
        Args:
            timestamp: UTC timestamp
            timezone_offset: User's timezone offset in minutes
        
        Returns:
            User's local date
        """
        if timezone_offset is not None:
            # Apply timezone offset (convert minutes to hours)
            from datetime import timedelta
            local_time = timestamp + timedelta(minutes=timezone_offset)
            return local_time.date()
        
        # Default to UTC date
        return timestamp.date()


# Global instance
recommendation_service = RecommendationService()