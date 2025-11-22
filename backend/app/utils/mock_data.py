"""Mock responses for testing without database."""
from datetime import datetime
from typing import List, Dict, Any
import uuid


def get_mock_wellness_score() -> Dict[str, Any]:
    """Return mock wellness score."""
    return {
        "id": str(uuid.uuid4()),
        "user_id": "test-user-123",
        "overall_score": 78,
        "emotional_score": 75,
        "physical_score": 82,
        "mental_score": 76,
        "spiritual_score": 79,
        "factors": {
            "sleep_quality": 8,
            "nutrition": 7,
            "exercise": 6,
            "stress_level": 4
        },
        "recommendations": [
            "Continue your meditation practice",
            "Try to get 30 minutes more sleep",
            "Add more vegetables to your diet"
        ],
        "created_at": datetime.now().isoformat()
    }


def get_mock_aura() -> Dict[str, Any]:
    """Return mock aura entry."""
    return {
        "id": str(uuid.uuid4()),
        "user_id": "test-user-123",
        "color": "blue",
        "intensity": 0.75,
        "chakra_balance": {
            "root": 0.8,
            "sacral": 0.7,
            "solar_plexus": 0.75,
            "heart": 0.9,
            "throat": 0.6,
            "third_eye": 0.85,
            "crown": 0.7
        },
        "computed_from": {
            "emotions": ["calm", "happy"],
            "activities": ["meditation", "yoga"]
        },
        "created_at": datetime.now().isoformat()
    }


def get_mock_dosha() -> Dict[str, Any]:
    """Return mock dosha assessment."""
    return {
        "id": str(uuid.uuid4()),
        "user_id": "test-user-123",
        "vata_score": 65,
        "pitta_score": 45,
        "kapha_score": 55,
        "dominant_dosha": "vata",
        "secondary_dosha": "kapha",
        "assessment_data": {
            "body_type": "thin",
            "digestion": "variable",
            "sleep_pattern": "light"
        },
        "created_at": datetime.now().isoformat()
    }


def get_mock_emotions() -> List[Dict[str, Any]]:
    """Return mock emotion logs."""
    emotions = ["joy", "calm", "excitement", "contentment", "peace"]
    return [
        {
            "id": str(uuid.uuid4()),
            "user_id": "test-user-123",
            "emotion": emotion,
            "intensity": 7 + i,
            "trigger": "meditation" if i % 2 == 0 else "yoga",
            "notes": f"Feeling {emotion} today",
            "detected_from": "manual",
            "created_at": datetime.now().isoformat()
        }
        for i, emotion in enumerate(emotions)
    ]


def get_mock_chat_response(message: str) -> Dict[str, Any]:
    """Generate mock chat response."""
    # Simple keyword-based responses
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["anxious", "stress", "worried"]):
        response = "I understand you're feeling anxious. Let's work through this together. I recommend a 10-minute breathing exercise to calm your mind. Would you like me to guide you through it?"
        emotion = "anxiety"
    elif any(word in message_lower for word in ["yoga", "exercise", "stretch"]):
        response = "Based on your dosha balance, I suggest a gentle Vinyasa flow. This will help balance your energy. Shall I create a personalized sequence for you?"
        emotion = "motivation"
    elif any(word in message_lower for word in ["eat", "food", "diet", "meal"]):
        response = "For your constitution, I recommend cooling foods like cucumber and sweet fruits. Would you like a detailed meal plan?"
        emotion = "curiosity"
    elif any(word in message_lower for word in ["sleep", "tired", "rest"]):
        response = "Quality sleep is essential for wellness. Try a calming bedtime routine with warm milk and gentle stretches. I can suggest specific techniques."
        emotion = "tired"
    else:
        user_snippet = message.strip()[:120] or "your recent note"
        response = (
            f"I hear you saying \"{user_snippet}\". I'm here to support your wellness journey "
            "with personalized yoga, nutrition, stress management, and mindfulness practices. "
            "Can you share a bit more about how you're feeling so I can offer something specific?"
        )
        emotion = "neutral"
    
    return {
        "message": {
            "id": str(uuid.uuid4()),
            "session_id": "test-session-123",
            "user_id": "test-user-123",
            "role": "assistant",
            "content": response,
            "emotion_detected": emotion,
            "crisis_detected": False,
            "created_at": datetime.now().isoformat()
        },
        "response": response,
        "session_id": "test-session-123",
        "crisis_detected": False,
        "emotion_detected": emotion
    }
