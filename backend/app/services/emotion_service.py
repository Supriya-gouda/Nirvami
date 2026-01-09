"""Emotion detection and analysis service."""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
from app.config import settings

logger = logging.getLogger(__name__)


class EmotionService:
    """Service for detecting and analyzing emotions from text."""
    
    # Emotion classification buckets for trend analysis
    POSITIVE_EMOTIONS = {
        'joy', 'happy', 'happiness', 'joyful', 'excited', 'excitement', 
        'calm', 'peaceful', 'relaxed', 'motivated', 'grateful', 'gratitude',
        'confident', 'confident', 'love', 'loved', 'content', 'satisfied',
        'hopeful', 'optimistic', 'proud', 'relief', 'relieved', 'inspired'
    }
    
    NEGATIVE_EMOTIONS = {
        'sad', 'sadness', 'sorrow', 'anger', 'angry', 'frustrated', 'frustration',
        'fear', 'fearful', 'afraid', 'anxiety', 'anxious', 'worried', 'stress',
        'stressed', 'guilt', 'guilty', 'shame', 'ashamed', 'overwhelmed',
        'depressed', 'depression', 'lonely', 'loneliness', 'disgust', 'disgusted',
        'jealous', 'jealousy', 'resentment', 'resentful', 'irritated', 'annoyed'
    }
    
    NEUTRAL_EMOTIONS = {
        'neutral', 'okay', 'fine', 'normal', 'indifferent', 'blank',
        'surprise', 'surprised', 'curious', 'confused', 'bored', 'tired'
    }
    
    def __init__(self, model_manager=None):
        """
        Initialize emotion service.
        
        Args:
            model_manager: Optional ML model manager for emotion detection
        """
        self.model_manager = model_manager
        self.emotion_labels = [
            'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral'
        ]
    
    def detect_emotion(self, text: str, source: str = "chat", min_confidence: float = None) -> Dict:
        """
        Detect emotion from text using ML model or rule-based fallback.
        
        ML-first approach:
        1. Try ML model if enabled and available
        2. Check confidence threshold (lower for journals: 0.35, default for chat: 0.45)
        3. Fallback to rules if ML fails or confidence too low
        
        Args:
            text: Input text to analyze
            source: Source of text ("chat" or "journal") - affects confidence threshold
            min_confidence: Optional override for minimum confidence threshold
            
        Returns:
            Dict with primary_emotion, confidence, emotion_scores, and source
        """
        # Determine confidence threshold based on source
        if min_confidence is not None:
            confidence_threshold = min_confidence
        elif source == "journal":
            confidence_threshold = 0.35  # Lower threshold for reflective journal text
        else:
            confidence_threshold = settings.EMOTION_CONFIDENCE_THRESHOLD  # 0.45 for chat (from config)
        
        logger.info(f"[EMOTION] Detecting emotion for {source} (threshold: {confidence_threshold})")
        
        # ML-first pipeline
        if settings.USE_ML_EMOTION_MODEL and self.model_manager:
            try:
                emotion_model = self.model_manager.get_emotion_model()
                if emotion_model is not None:
                    ml_result = self._detect_with_ml(text, emotion_model, source)
                    
                    logger.info(f"[EMOTION] ML returned: {ml_result['primary_emotion']} @ {ml_result['confidence']:.2f}")
                    
                    # Check confidence threshold
                    if ml_result['confidence'] >= confidence_threshold:
                        logger.info(f"[EMOTION] ML confidence {ml_result['confidence']:.2f} >= {confidence_threshold} → ACCEPTED")
                        return ml_result
                    else:
                        logger.warning(f"[EMOTION] ML confidence {ml_result['confidence']:.2f} < {confidence_threshold} → falling back to rules")
                        return self._detect_with_rules(text)
            except Exception as e:
                logger.error(f"[EMOTION] ML detection failed: {e}, falling back to rule-based detection")
                logger.exception(e)
                return self._detect_with_rules(text)
        
        # Fallback to rule-based detection
        logger.warning(f"[EMOTION] ML not available, using rule-based detection")
        return self._detect_with_rules(text)
    
    def _detect_with_ml(self, text: str, emotion_model, source: str = "chat") -> Dict:
        """Use ML model for emotion detection with label mapping and normalization."""
        # Log original text length
        logger.info(f"[EMOTION] Text length: {len(text)} chars")
        
        # Validate text - allow short messages (minimum 3 chars for model)
        if len(text.strip()) < 3:
            logger.warning(f"[EMOTION] Text too short ({len(text)} chars), returning neutral")
            return {
                'primary_emotion': 'neutral',
                'emotion_type': 'neutral',
                'confidence': 0.5,
                'emotion_scores': {'neutral': 1.0},
                'all_scores': {'neutral': 1.0},
                'source': 'ml'
            }
        
        # For chat messages, truncate to prevent token overflow
        # For journal entries, caller should handle this
        # Max 512 tokens ~ 2000 chars for transformer models
        if len(text) > 2000:
            logger.info(f"[EMOTION] Truncating text from {len(text)} to 2000 chars for ML model")
            text = text[:2000]
        
        # Run inference with go_emotions model
        logger.info(f"[EMOTION] Using go_emotions model (28 emotions)")
        results = emotion_model(text)[0]
        
        # Get all emotion scores from go_emotions (28 labels)
        emotion_scores = {item['label'].lower(): float(item['score']) for item in results}
        
        # Get top emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[primary_emotion]
        
        # Log top 3 emotions
        top_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        top_str = ", ".join([f"{e}={s:.2f}" for e, s in top_emotions])
        logger.info(f"[EMOTION][GO] Detected: {primary_emotion} ({confidence:.2f}) | Top 3: {top_str}")
        
        # Post-processing: If ML detected "neutral" but text has strong emotion keywords,
        # check for keyword-based override (prevents false neutrals)
        if primary_emotion == 'neutral' and confidence < 0.70:
            text_lower = text.lower()
            keyword_override = self._check_keyword_override(text_lower, emotion_scores)
            if keyword_override:
                logger.info(f"[EMOTION] Overriding neutral with keyword-based: {keyword_override['emotion']} (found: {keyword_override['keywords']})")
                primary_emotion = keyword_override['emotion']
                # Boost confidence for keyword match
                confidence = max(emotion_scores.get(primary_emotion, 0.5), 0.60)
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_type': primary_emotion,  # Backward compatibility
            'confidence': confidence,
            'emotion_scores': emotion_scores,
            'all_scores': emotion_scores,  # Backward compatibility
            'source': 'ml'
        }
    
    def _check_keyword_override(self, text_lower: str, emotion_scores: Dict) -> Optional[Dict]:
        """Check if text contains strong emotion keywords that should override neutral."""
        # Strong emotion keywords that should override neutral detection
        keyword_map = {
            'nervousness': ['stressed', 'stress', 'anxious', 'anxiety', 'tensed', 'tense', 'overwhelmed'],
            'fear': ['afraid', 'scared', 'terrified', 'panic'],
            'sadness': ['sad', 'depressed', 'miserable', 'devastated', 'hopeless'],
            'anger': ['angry', 'furious', 'enraged', 'outraged'],
            'joy': ['happy', 'excited', 'delighted', 'thrilled'],
            'annoyance': ['annoyed', 'irritated', 'frustrated'],
        }
        
        for emotion, keywords in keyword_map.items():
            found_keywords = [kw for kw in keywords if kw in text_lower]
            if found_keywords:
                # Return the emotion with highest score from alternatives
                return {
                    'emotion': emotion,
                    'keywords': found_keywords
                }
        
        return None
    
    def detect_contextual_emotion(self, texts: List[str]) -> Dict:
        """
        Detect emotion from a sequence of texts (contextual analysis).
        Uses last 3 messages for context to prevent token overflow.
        
        Args:
            texts: List of text messages to analyze together
            
        Returns:
            Dict with primary_emotion, confidence, emotion_scores, and source
        """
        if not texts:
            return {
                'primary_emotion': 'neutral',
                'emotion_type': 'neutral',  # Backward compatibility
                'confidence': 0.5,
                'emotion_scores': {'neutral': 1.0},
                'all_scores': {'neutral': 1.0},  # Backward compatibility
                'source': 'rules'
            }
        
        # Use last 3 messages max for context (prevent token overflow)
        context_texts = texts[-3:] if len(texts) > 3 else texts
        
        # Combine with emphasis on most recent message
        combined_text = " ".join(context_texts[:-1] + [context_texts[-1]] * 2)
        
        return self.detect_emotion(combined_text)

    def _detect_with_rules(self, text: str) -> Dict:
        """Rule-based emotion detection as fallback."""
        text_lower = text.lower()
        
        # Keyword-based detection
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'excellent', 'delighted', 'cheerful', 'thrilled'],
            'sadness': ['sad', 'depressed', 'down', 'unhappy', 'miserable', 'lonely', 'crying', 'disappointed', 'hopeless', 'devastated'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated', 'outraged', 'enraged'],
            'fear': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'panic', 'terrified', 'tensed', 'tense', 'stressed', 'stress', 'overwhelmed', 'concern', 'concerned', 'uneasy', 'apprehensive'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'unexpected', 'startled'],
            'disgust': ['disgusted', 'gross', 'awful', 'terrible', 'horrible', 'revolting'],
        }
        
        scores = {'neutral': 0.5}
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                scores[emotion] = min(0.3 + (count * 0.2), 0.95)
        
        # Get dominant emotion
        dominant_emotion = max(scores, key=scores.get)
        
        return {
            'primary_emotion': dominant_emotion,
            'emotion_type': dominant_emotion,  # Backward compatibility
            'confidence': float(scores[dominant_emotion]),
            'emotion_scores': scores,
            'all_scores': scores,  # Backward compatibility
            'source': 'rules'
        }
    
    def create_emotion_log(
        self,
        user_id: str,
        emotion_type: str,
        confidence: float,
        all_scores: Dict,
        source: str = 'text',
        message_id: Optional[str] = None
    ) -> Dict:
        """
        Create emotion log entry.
        
        Args:
            user_id: User ID
            emotion_type: Detected emotion
            confidence: Confidence score
            all_scores: All emotion scores
            source: Detection source (text/voice/manual)
            message_id: Optional related message ID
            
        Returns:
            Emotion log data
        """
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'message_id': message_id,
            'emotion_type': emotion_type,
            'confidence': confidence,
            'all_scores': all_scores,
            'source': source,
            'created_at': datetime.utcnow().isoformat()
        }
    
    def analyze_sentiment_trend(self, emotion_logs: List[Dict]) -> Dict:
        """
        Analyze emotion trends from logs.
        
        Args:
            emotion_logs: List of emotion log entries
            
        Returns:
            Trend analysis with dominant emotion and distribution
        """
        if not emotion_logs:
            return {
                'dominant_emotion': 'neutral',
                'emotion_distribution': {},
                'average_valence': 0.0,
                'total_entries': 0
            }
        
        # Count emotions
        emotion_counts = {}
        total_valence = 0.0
        
        # Valence mapping (positive to negative)
        valence_map = {
            'joy': 1.0,
            'surprise': 0.5,
            'neutral': 0.0,
            'fear': -0.5,
            'disgust': -0.6,
            'sadness': -0.8,
            'anger': -0.9
        }
        
        for log in emotion_logs:
            emotion = log.get('emotion_type', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_valence += valence_map.get(emotion, 0.0)
        
        total = len(emotion_logs)
        distribution = {k: v / total for k, v in emotion_counts.items()}
        dominant = max(emotion_counts, key=emotion_counts.get)
        
        return {
            'dominant_emotion': dominant,
            'emotion_distribution': distribution,
            'average_valence': total_valence / total,
            'total_entries': total
        }
    
    def classify_emotion(self, emotion: str) -> str:
        """
        Classify an emotion into positive, negative, or neutral bucket.
        
        Args:
            emotion: Emotion string (e.g., 'joy', 'sad', 'neutral')
            
        Returns:
            Classification: 'positive', 'negative', or 'neutral'
        """
        emotion_lower = emotion.lower().strip()
        
        if emotion_lower in self.POSITIVE_EMOTIONS:
            return 'positive'
        elif emotion_lower in self.NEGATIVE_EMOTIONS:
            return 'negative'
        else:
            return 'neutral'
    
    def compute_daily_emotion_summary(self, emotion_logs: List[Dict], target_date: date) -> Dict:
        """
        Compute daily emotion percentages using confidence-weighted sums.
        
        This method implements the emotion trend logic:
        1. Filter emotions for the target date
        2. Classify each emotion into positive/negative/neutral
        3. Weight by confidence score
        4. Calculate percentages that sum to 100%
        
        Args:
            emotion_logs: List of emotion log entries for the day
            target_date: The date to compute summary for
            
        Returns:
            Dict with positive_percent, negative_percent, neutral_percent,
            and total_weighted_count
        """
        if not emotion_logs:
            # Return balanced neutral state if no emotions logged
            return {
                'positive_percent': 0.0,
                'negative_percent': 0.0,
                'neutral_percent': 100.0,
                'total_weighted_count': 0.0
            }
        
        # Initialize weighted sums
        positive_weighted = 0.0
        negative_weighted = 0.0
        neutral_weighted = 0.0
        
        # Process each emotion log
        for log in emotion_logs:
            emotion_type = log.get('emotion_type', 'neutral')
            confidence = float(log.get('confidence', 0.5))
            
            # Classify and add weighted score
            classification = self.classify_emotion(emotion_type)
            
            if classification == 'positive':
                positive_weighted += confidence
            elif classification == 'negative':
                negative_weighted += confidence
            else:
                neutral_weighted += confidence
        
        # Calculate total
        total_weighted = positive_weighted + negative_weighted + neutral_weighted
        
        if total_weighted == 0:
            # Shouldn't happen but handle edge case
            return {
                'positive_percent': 0.0,
                'negative_percent': 0.0,
                'neutral_percent': 100.0,
                'total_weighted_count': 0.0
            }
        
        # Calculate percentages (sum = 100%)
        positive_percent = (positive_weighted / total_weighted) * 100.0
        negative_percent = (negative_weighted / total_weighted) * 100.0
        neutral_percent = (neutral_weighted / total_weighted) * 100.0
        
        # Round to 2 decimal places
        positive_percent = round(positive_percent, 2)
        negative_percent = round(negative_percent, 2)
        neutral_percent = round(neutral_percent, 2)
        
        # Ensure exact sum of 100.00 by adjusting the largest component
        total_percent = positive_percent + negative_percent + neutral_percent
        
        if abs(total_percent - 100.0) > 0.001:
            # Find the largest component and adjust it
            max_val = max(positive_percent, negative_percent, neutral_percent)
            adjustment = 100.0 - total_percent
            
            if positive_percent == max_val:
                positive_percent = round(positive_percent + adjustment, 2)
            elif negative_percent == max_val:
                negative_percent = round(negative_percent + adjustment, 2)
            else:
                neutral_percent = round(neutral_percent + adjustment, 2)
        
        return {
            'positive_percent': positive_percent,
            'negative_percent': negative_percent,
            'neutral_percent': neutral_percent,
            'total_weighted_count': round(total_weighted, 2)
        }
    
    def store_daily_emotion_summary(
        self,
        supabase,
        user_id: str,
        target_date: date,
        summary: Dict
    ) -> Dict:
        """
        Store or update daily emotion summary in database.
        
        Dynamic updating rule:
        - If date == today: always update (upsert)
        - If date < today: only create if doesn't exist (don't update past)
        
        Args:
            supabase: Supabase client
            user_id: User ID
            target_date: Date for the summary
            summary: Computed summary dict with percentages
            
        Returns:
            Stored summary record
        """
        today = date.today()
        date_str = target_date.isoformat()
        
        # Check if record exists
        existing = supabase.table("daily_emotion_summary")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("date", date_str)\
            .execute()
        
        record_exists = existing.data and len(existing.data) > 0
        
        # Prepare data
        summary_data = {
            'user_id': user_id,
            'date': date_str,
            'positive_percent': summary['positive_percent'],
            'negative_percent': summary['negative_percent'],
            'neutral_percent': summary['neutral_percent'],
            'total_weighted_count': summary['total_weighted_count'],
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Dynamic updating logic
        if target_date == today:
            # Today: always update
            if record_exists:
                # Update existing record
                result = supabase.table("daily_emotion_summary")\
                    .update(summary_data)\
                    .eq("user_id", user_id)\
                    .eq("date", date_str)\
                    .execute()
                logger.info(f"Updated emotion summary for today: {date_str}")
            else:
                # Insert new record
                result = supabase.table("daily_emotion_summary")\
                    .insert(summary_data)\
                    .execute()
                logger.info(f"Created emotion summary for today: {date_str}")
        else:
            # Past date: only create if doesn't exist
            if not record_exists:
                result = supabase.table("daily_emotion_summary")\
                    .insert(summary_data)\
                    .execute()
                logger.info(f"Created emotion summary for past date: {date_str}")
            else:
                # Don't update past dates
                logger.info(f"Skipping update for past date: {date_str} (already exists)")
                result = existing
        
        return result.data[0] if result.data else None
    
    def update_emotion_trends(
        self,
        supabase,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """
        Update emotion trends for a date range by computing daily summaries.
        
        This is useful for:
        - Backfilling historical data
        - Recalculating today's trends
        - Batch processing
        
        Args:
            supabase: Supabase client
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of daily emotion summaries
        """
        summaries = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            next_date_str = (current_date + timedelta(days=1)).isoformat()
            
            # Fetch all emotions for this day
            emotion_logs = supabase.table("emotion_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("created_at", f"{date_str}T00:00:00")\
                .lt("created_at", f"{next_date_str}T00:00:00")\
                .execute()
            
            # Compute summary
            summary = self.compute_daily_emotion_summary(
                emotion_logs.data or [],
                current_date
            )
            
            # Store summary
            if summary['total_weighted_count'] > 0:  # Only store if there are emotions
                stored = self.store_daily_emotion_summary(
                    supabase,
                    user_id,
                    current_date,
                    summary
                )
                if stored:
                    summaries.append(stored)
            
            current_date += timedelta(days=1)
        
        return summaries


def get_emotion_service(model_manager=None):
    """Get emotion service instance."""
    return EmotionService(model_manager)
