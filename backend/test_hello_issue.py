"""Test specific issue: "Hello" being detected as anger."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.emotion_service import EmotionService
from app.ml.model_manager import ModelManager
from app.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_hello():
    """Test the specific case: 'Hello' message."""
    
    print("\n" + "="*80)
    print("🧪 TESTING 'Hello' MESSAGE ISSUE")
    print("="*80)
    
    # Load ML model
    print("\n⏳ Loading ML models...")
    model_manager = ModelManager()
    await model_manager.load_models()
    print("✅ Models loaded")
    
    emotion_service = EmotionService(model_manager)
    
    # Test cases that might be problematic
    test_cases = [
        "Hello",
        "Hi",
        "Hey",
        "Hello there",
        "Hi, how are you?",
        "Greetings",
        "",  # Empty
        "a",  # Single char
        "ok",  # Very short
    ]
    
    print("\n" + "-"*80)
    print("Testing short messages/greetings:")
    print("-"*80)
    
    for text in test_cases:
        print(f"\nText: \"{text}\" (length: {len(text)})")
        
        if len(text) < 5:
            print(f"   ⚠️  Message too short (< 5 chars) - should use neutral fallback")
        
        result = emotion_service.detect_emotion(text)
        
        print(f"   → Emotion: {result['primary_emotion']}")
        print(f"   → Confidence: {result['confidence']:.3f}")
        print(f"   → Source: {result['source']}")
        
        # Check if it's detecting anger incorrectly
        if result['primary_emotion'] == 'anger' and text.lower() in ['hello', 'hi', 'hey']:
            print(f"   ❌ ERROR: Greeting detected as ANGER!")
        elif result['primary_emotion'] in ['neutral', 'joy']:
            print(f"   ✅ Correct: Greeting should be neutral or positive")
    
    # Test contextual with Hello
    print("\n" + "-"*80)
    print("Testing 'Hello' in contextual mode (first message):")
    print("-"*80)
    
    conversation = ["Hello"]
    result = emotion_service.detect_contextual_emotion(conversation)
    
    print(f"\n   → Emotion: {result['primary_emotion']}")
    print(f"   → Confidence: {result['confidence']:.3f}")
    print(f"   → Source: {result['source']}")
    
    if result['primary_emotion'] == 'anger':
        print(f"   ❌ ERROR: 'Hello' detected as ANGER in contextual mode!")
    
    # Test with empty history (simulating first message in chat)
    print("\n" + "-"*80)
    print("Simulating chat.py logic for 'Hello' (first message):")
    print("-"*80)
    
    message_content = "Hello"
    recent_user_msgs = []  # No history
    recent_user_msgs.append(message_content)
    
    print(f"\nMessage: '{message_content}'")
    print(f"History length: {len(recent_user_msgs) - 1}")
    print(f"Message length: {len(message_content)}")
    
    # Simulate chat.py logic
    if len(message_content) < 5 and len(recent_user_msgs) == 1:
        print("   → Using hardcoded neutral (message < 5 chars, first message)")
        emotion_data = {
            'emotion_type': 'neutral',
            'confidence': 0.5,
            'all_scores': {'neutral': 1.0},
            'source': 'hardcoded'
        }
    else:
        print("   → Using ML/contextual detection")
        emotion_data = emotion_service.detect_contextual_emotion(recent_user_msgs)
    
    print(f"\n   → Final Emotion: {emotion_data.get('emotion_type', emotion_data.get('primary_emotion'))}")
    print(f"   → Confidence: {emotion_data['confidence']:.3f}")
    print(f"   → Source: {emotion_data.get('source', 'unknown')}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_hello())
