"""Test script to verify ML-first emotion detection."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.emotion_service import EmotionService
from app.ml.model_manager import ModelManager
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_emotion_detection():
    """Test ML-first emotion detection with fallback."""
    
    print("\n" + "="*80)
    print("🧪 TESTING ML-FIRST EMOTION DETECTION")
    print("="*80)
    
    # Test cases
    test_cases = [
        "I'm so happy and excited about my new job!",
        "I feel really sad and lonely today",
        "This makes me so angry and frustrated",
        "I'm worried and anxious about the exam",
        "What a wonderful surprise!",
        "That's disgusting and terrible",
        "Just a regular day, nothing special",
        "I'm feeling a bit down but trying to stay positive",
    ]
    
    print(f"\n📋 Configuration:")
    print(f"   USE_ML_EMOTION_MODEL: {settings.USE_ML_EMOTION_MODEL}")
    print(f"   EMOTION_CONFIDENCE_THRESHOLD: {settings.EMOTION_CONFIDENCE_THRESHOLD}")
    print(f"   ENABLE_ML_MODELS: {settings.ENABLE_ML_MODELS}")
    
    # Test with ML model (if available)
    print("\n" + "-"*80)
    print("🤖 Testing WITH ML Model")
    print("-"*80)
    
    model_manager = None
    if settings.ENABLE_ML_MODELS:
        try:
            print("\n⏳ Loading ML models...")
            model_manager = ModelManager()
            await model_manager.load_models()
            print("✅ ML models loaded successfully")
        except Exception as e:
            print(f"⚠️  ML models failed to load: {e}")
            print("   Will use rule-based fallback only")
    
    emotion_service = EmotionService(model_manager)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Text: \"{text}\"")
        result = emotion_service.detect_emotion(text)
        
        print(f"   → Emotion: {result['primary_emotion']}")
        print(f"   → Confidence: {result['confidence']:.3f}")
        print(f"   → Source: {result['source']}")
        print(f"   → Top 3 scores: {dict(sorted(result['emotion_scores'].items(), key=lambda x: x[1], reverse=True)[:3])}")
    
    # Test contextual detection
    print("\n" + "-"*80)
    print("🔗 Testing Contextual Detection (Last 3 Messages)")
    print("-"*80)
    
    conversation = [
        "I had a bad day at work",
        "My boss yelled at me in front of everyone",
        "I feel humiliated and really angry now"
    ]
    
    print(f"\nConversation:")
    for msg in conversation:
        print(f"   • {msg}")
    
    result = emotion_service.detect_contextual_emotion(conversation)
    print(f"\n   → Combined Emotion: {result['primary_emotion']}")
    print(f"   → Confidence: {result['confidence']:.3f}")
    print(f"   → Source: {result['source']}")
    
    # Test without ML (force rule-based)
    print("\n" + "-"*80)
    print("📝 Testing Rule-Based Fallback (No ML)")
    print("-"*80)
    
    emotion_service_no_ml = EmotionService(None)
    
    text = "I'm feeling really happy and joyful today!"
    print(f"\nText: \"{text}\"")
    result = emotion_service_no_ml.detect_emotion(text)
    
    print(f"   → Emotion: {result['primary_emotion']}")
    print(f"   → Confidence: {result['confidence']:.3f}")
    print(f"   → Source: {result['source']}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_emotion_detection())
