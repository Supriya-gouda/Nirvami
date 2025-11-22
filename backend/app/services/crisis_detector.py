"""Crisis detection service for identifying distress signals."""
import re
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)

# Crisis keywords and patterns
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "better off dead", "no reason to live", "can't go on", "hurt myself",
    "self harm", "cut myself", "overdose", "end it all", "goodbye world",
    "final goodbye", "hopeless", "can't take it", "give up"
]

DISTRESS_PATTERNS = [
    r"want.*die",
    r"kill.*myself",
    r"end.*life",
    r"hurt.*myself",
    r"can'?t.*anymore",
    r"no.*point.*living",
    r"everyone.*better.*without",
]

# High severity emotional states
HIGH_RISK_EMOTIONS = ["sadness", "anger", "fear"]
HIGH_RISK_THRESHOLD = 0.7  # Confidence threshold


class CrisisDetector:
    """Detects crisis situations from text and emotional data."""
    
    @staticmethod
    def detect_crisis(text: str, emotion_data: dict = None) -> Tuple[bool, str, List[str]]:
        """
        Detect if text or emotions indicate a crisis.
        
        Args:
            text: User message text
            emotion_data: Dict with emotion scores
            
        Returns:
            Tuple of (is_crisis, severity, triggers)
        """
        text_lower = text.lower()
        triggers = []
        is_crisis = False
        severity = "low"
        
        # Check for crisis keywords
        for keyword in CRISIS_KEYWORDS:
            if keyword in text_lower:
                triggers.append(f"keyword: {keyword}")
                is_crisis = True
                severity = "critical"
        
        # Check patterns
        if not is_crisis:
            for pattern in DISTRESS_PATTERNS:
                if re.search(pattern, text_lower):
                    triggers.append(f"pattern: {pattern}")
                    is_crisis = True
                    severity = "high"
        
        # Check emotional state
        if emotion_data:
            dominant = emotion_data.get("dominant_emotion", "").lower()
            confidence = emotion_data.get("confidence", 0)
            
            if dominant in HIGH_RISK_EMOTIONS and confidence >= HIGH_RISK_THRESHOLD:
                triggers.append(f"emotion: {dominant} ({confidence:.2f})")
                if not is_crisis:
                    is_crisis = True
                    severity = "medium"
        
        # Check for repeated negative expressions
        negative_words = ["hopeless", "worthless", "useless", "failure", "alone", "trapped"]
        negative_count = sum(1 for word in negative_words if word in text_lower)
        if negative_count >= 3:
            triggers.append(f"multiple negative expressions ({negative_count})")
            if not is_crisis:
                is_crisis = True
                severity = "medium"
        
        if is_crisis:
            logger.warning(f"Crisis detected: severity={severity}, triggers={triggers}")
        
        return is_crisis, severity, triggers
    
    @staticmethod
    def get_crisis_response() -> str:
        """Get appropriate crisis response message."""
        return (
            "I'm concerned about what you're sharing. Your wellbeing is important. "
            "Please consider reaching out to a crisis helpline:\n\n"
            "🆘 National Suicide Prevention Lifeline: 988 (US)\n"
            "🆘 Crisis Text Line: Text HOME to 741741\n"
            "🆘 International: findahelpline.com\n\n"
            "Would you like me to help you find local resources?"
        )
