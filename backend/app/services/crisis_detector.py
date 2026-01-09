"""Crisis detection service for identifying distress signals."""
import re
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)

# Crisis keywords - ONLY for genuine suicide/self-harm situations
# These must be VERY SPECIFIC to avoid false positives
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "killing myself",
    "end my life", "ending my life", "want to die", "wanna die",
    "better off dead", "no reason to live", "can't go on",
    "hurt myself", "hurting myself", "self harm", "self-harm",
    "cut myself", "cutting myself", "overdose",
    "end it all", "goodbye world", "final goodbye"
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
        
        # ONLY check for explicit crisis keywords (suicide, self-harm, etc.)
        # Do NOT trigger on emotions or patterns - only explicit crisis language
        for keyword in CRISIS_KEYWORDS:
            if keyword in text_lower:
                triggers.append(f"keyword: {keyword}")
                is_crisis = True
                severity = "critical"
                logger.critical(f"🚨 CRISIS KEYWORD DETECTED: {keyword}")
        
        # Log emotion for debugging but DO NOT use it for crisis detection
        if emotion_data:
            emotion_type = emotion_data.get("emotion_type") or emotion_data.get("primary_emotion", "").lower()
            confidence = emotion_data.get("confidence", 0)
            logger.info(f"[CRISIS CHECK] Emotion: {emotion_type} @ {confidence:.2f} (info only, not used for crisis detection)")
        
        if is_crisis:
            logger.error(f"🚨 CRISIS DETECTED: severity={severity}, triggers={triggers}")
        
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
