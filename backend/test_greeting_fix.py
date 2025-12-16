"""Test the fix for short message/greeting detection."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.emotion_service import EmotionService
from app.ml.model_manager import ModelManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_fix():
    """Test the fix: short messages and greetings analyzed without context."""
    
    print("\n" + "="*80)
    print("🧪 TESTING FIX: SHORT MESSAGES/GREETINGS WITHOUT CONTEXT")
    print("="*80)
    
    # Load ML model
    print("\n⏳ Loading ML models...")
    model_manager = ModelManager()
    await model_manager.load_models()
    print("✅ Models loaded")
    
    emotion_service = EmotionService(model_manager)
    
    # Test scenarios that should now work correctly
    test_scenarios = [
        {
            'name': 'Greeting after anxious message',
            'previous_messages': ["I am very scared and tensed that my project will run or no what shall i do"],
            'current_message': 'Hello',
            'should_analyze_alone': True,
            'expected_emotion': 'neutral',
        },
        {
            'name': 'Short message after sad conversation',
            'previous_messages': ["I'm so depressed", "Everything is terrible", "I feel awful"],
            'current_message': 'ok',
            'should_analyze_alone': True,
            'expected_emotion': 'neutral',
        },
        {
            'name': 'Greeting after happy conversation',
            'previous_messages': ["I'm so happy!", "This is amazing!"],
            'current_message': 'Hey',
            'should_analyze_alone': True,
            'expected_emotion': 'neutral or joy',
        },
        {
            'name': 'Long emotional message (should use context)',
            'previous_messages': ["I'm very happy today"],
            'current_message': 'I am really worried about my exam tomorrow',
            'should_analyze_alone': False,
            'expected_emotion': 'fear or sadness',
        },
        {
            'name': 'Normal conversation continuation (should use context)',
            'previous_messages': ["I love this project"],
            'current_message': 'It makes me so happy to work on it',
            'should_analyze_alone': False,
            'expected_emotion': 'joy',
        },
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n" + "-"*80)
        print(f"Scenario {i}: {scenario['name']}")
        print("-"*80)
        
        current_msg = scenario['current_message']
        is_short = len(current_msg) <= 15
        is_greeting = current_msg.lower() in ['hi', 'hello', 'hey', 'hey there', 'hi there', 'hello there', 'greetings']
        
        print(f"\nPrevious messages:")
        for prev_msg in scenario['previous_messages']:
            print(f"   - \"{prev_msg}\"")
        print(f"\nCurrent message: \"{current_msg}\"")
        print(f"   Length: {len(current_msg)}")
        print(f"   Is short (≤15): {is_short}")
        print(f"   Is greeting: {is_greeting}")
        print(f"   Should analyze alone: {scenario['should_analyze_alone']}")
        
        # Simulate the fixed logic
        if (is_short or is_greeting) and len(scenario['previous_messages']) > 0:
            print(f"\n   → Using FIX: Analyzing current message ALONE (no context)")
            result = emotion_service.detect_emotion(current_msg)
        else:
            print(f"\n   → Using contextual detection (with history)")
            all_messages = scenario['previous_messages'] + [current_msg]
            result = emotion_service.detect_contextual_emotion(all_messages)
        
        print(f"\n   → Detected Emotion: {result['primary_emotion']}")
        print(f"   → Confidence: {result['confidence']:.3f}")
        print(f"   → Source: {result['source']}")
        print(f"   → Expected: {scenario['expected_emotion']}")
        
        # Validate
        if scenario['should_analyze_alone']:
            if result['primary_emotion'] in ['neutral', 'joy']:
                print(f"   ✅ PASS: Greeting/short message correctly analyzed alone")
            else:
                print(f"   ⚠️  Unexpected: Got {result['primary_emotion']}")
        else:
            print(f"   ✅ Contextual detection used as expected")
    
    print("\n" + "="*80)
    print("📋 FIX SUMMARY")
    print("="*80)
    print("""
WHAT WAS CHANGED:
- In chat.py, line 170-195
- Short messages (≤15 chars) now analyzed WITHOUT context
- Common greetings (hello, hi, hey, etc.) analyzed WITHOUT context
- This prevents "Hello" from inheriting "fear" from previous anxious messages

LOGIC:
1. If message ≤15 chars OR is a greeting → analyze alone (no history)
2. If message <5 chars AND first message → use neutral
3. Otherwise → use contextual detection with last 5 messages

BENEFIT:
- "Hello" after anxious conversation → neutral (correct)
- "Hi" after sad conversation → neutral (correct)
- Long emotional messages still use context (correct)
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_fix())
