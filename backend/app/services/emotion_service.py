"""Emotion detection and analysis service."""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid
from app.config import settings

logger = logging.getLogger(__name__)

# Label mapping from model output to internal emotion names
LABEL_MAP = {
    "joy": "joy",
    "sadness": "sadness",
    "anger": "anger",
    "fear": "fear",
    "surprise": "surprise",
    "disgust": "disgust",
    "neutral": "neutral"
}


class EmotionService:
    """Service for detecting and analyzing emotions from text."""
    
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
        2. Check confidence threshold (lower for journals: 0.40, higher for chat: 0.55)
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
            confidence_threshold = 0.40  # Lower threshold for reflective journal text
        else:
            confidence_threshold = settings.EMOTION_CONFIDENCE_THRESHOLD  # 0.55 for chat
        
        logger.info(f"[EMOTION] Detecting emotion for {source} (threshold: {confidence_threshold})")
        
        # ML-first pipeline
        if settings.USE_ML_EMOTION_MODEL and self.model_manager:
            try:
                emotion_model = self.model_manager.get_emotion_model()
                if emotion_model is not None:
                    ml_result = self._detect_with_ml(text, emotion_model)
                    
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
    
    def _detect_with_ml(self, text: str, emotion_model) -> Dict:
        """Use ML model for emotion detection with label mapping and normalization."""
        # Log original text length
        logger.info(f"[EMOTION] Text length: {len(text)} chars")
        
        # Validate text
        if len(text.strip()) < 10:
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
        
        # Run inference
        results = emotion_model(text)[0]
        
        # Map model labels to internal emotion names and normalize scores
        mapped_scores = {}
        for item in results:
            model_label = item['label'].lower()
            internal_label = LABEL_MAP.get(model_label, 'neutral')
            score = float(item['score'])
            
            # Aggregate scores if model returns multiple labels for same emotion
            if internal_label in mapped_scores:
                mapped_scores[internal_label] = max(mapped_scores[internal_label], score)
            else:
                mapped_scores[internal_label] = score
        
        # Get emotion with highest confidence
        primary_emotion = max(mapped_scores, key=mapped_scores.get)
        confidence = mapped_scores[primary_emotion]
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_type': primary_emotion,  # Backward compatibility
            'confidence': confidence,
            'emotion_scores': mapped_scores,
            'all_scores': mapped_scores,  # Backward compatibility
            'source': 'ml'
        }
    
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
            'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'excellent'],
            'sadness': ['sad', 'depressed', 'down', 'unhappy', 'miserable', 'lonely', 'crying'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated'],
            'fear': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'panic', 'terrified'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'unexpected'],
            'disgust': ['disgusted', 'gross', 'awful', 'terrible', 'horrible'],
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


def get_emotion_service(model_manager=None):
    """Get emotion service instance."""
    return EmotionService(model_manager)
