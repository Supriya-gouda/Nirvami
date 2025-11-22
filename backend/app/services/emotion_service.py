"""Emotion detection and analysis service."""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


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
    
    def detect_emotion(self, text: str) -> Dict:
        """
        Detect emotion from text using ML model or rule-based fallback.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with emotion_type, confidence, and all_scores
        """
        if self.model_manager and self.model_manager.emotion_pipeline:
            return self._detect_with_ml(text)
        else:
            return self._detect_with_rules(text)
    
    def _detect_with_ml(self, text: str) -> Dict:
        """Use ML model for emotion detection."""
        try:
            results = self.model_manager.emotion_pipeline(text)[0]
            
            # Convert to our format
            all_scores = {item['label']: item['score'] for item in results}
            
            # Get dominant emotion
            dominant = max(results, key=lambda x: x['score'])
            
            return {
                'emotion_type': dominant['label'],
                'confidence': float(dominant['score']),
                'all_scores': all_scores
            }
        except Exception as e:
            logger.error(f"ML emotion detection failed: {e}")
            return self._detect_with_rules(text)
    
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
            'emotion_type': dominant_emotion,
            'confidence': float(scores[dominant_emotion]),
            'all_scores': scores
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
