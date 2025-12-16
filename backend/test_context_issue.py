"""Test contextual detection with previous emotional messages."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.emotion_service import EmotionService
from app.ml.model_manager import ModelManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_context_issue():
    """Simulate the exact scenario from the screenshot."""
    
    print("\n" + "="*80)
    print("🧪 TESTING CONTEXTUAL DETECTION WITH PREVIOUS EMOTIONAL MESSAGES")
    print("="*80)
    
    # Load ML model
    print("\n⏳ Loading ML models...")
    model_manager = ModelManager()
    await model_manager.load_models()
    print("✅ Models loaded")
    
    emotion_service = EmotionService(model_manager)
    
    # Simulate the scenario from the screenshot:
    # Previous message: About project anxiety/fear
    # Current message: "Hello"
    
    print("\n" + "-"*80)
    print("Scenario 1: 'Hello' ALONE (no context)")
    print("-"*80)
    
    messages_alone = ["Hello"]
    result1 = emotion_service.detect_contextual_emotion(messages_alone)
    
    print(f"\nMessages: {messages_alone}")
    print(f"   → Emotion: {result1['primary_emotion']}")
    print(f"   → Confidence: {result1['confidence']:.3f}")
    print(f"   → Source: {result1['source']}")
    
    if result1['primary_emotion'] == 'anger':
        print(f"   ❌ ERROR: 'Hello' alone detected as ANGER!")
    else:
        print(f"   ✅ CORRECT")
    
    print("\n" + "-"*80)
    print("Scenario 2: 'Hello' WITH CONTEXT (previous anxious message)")
    print("-"*80)
    
    # This simulates what chat.py line 175 does:
    # recent_user_msgs = [msg["content"] for msg in chat_history if msg["role"] == "user"][-5:]
    # recent_user_msgs.append(message_req.content)
    
    messages_with_context = [
        "I am very scared and tensed that my project will run or no what shall i do",
        "Hello"
    ]
    
    result2 = emotion_service.detect_contextual_emotion(messages_with_context)
    
    print(f"\nMessages: ")
    for i, msg in enumerate(messages_with_context, 1):
        print(f"   {i}. \"{msg}\"")
    
    print(f"\n   → Emotion: {result2['primary_emotion']}")
    print(f"   → Confidence: {result2['confidence']:.3f}")
    print(f"   → Source: {result2['source']}")
    
    if result2['primary_emotion'] in ['fear', 'anger', 'sadness']:
        print(f"   ⚠️  CONTEXT INFLUENCED: 'Hello' inherited emotion from previous message!")
        print(f"   This is why the screenshot shows wrong emotion.")
    else:
        print(f"   ✅ Context properly handled")
    
    print("\n" + "-"*80)
    print("Scenario 3: Multiple anxious messages, then 'Hello'")
    print("-"*80)
    
    messages_multi_context = [
        "I'm really worried about my deadline",
        "I feel so anxious and stressed",
        "What if I fail?",
        "I'm scared",
        "Hello"
    ]
    
    result3 = emotion_service.detect_contextual_emotion(messages_multi_context)
    
    print(f"\nMessages: ")
    for i, msg in enumerate(messages_multi_context, 1):
        print(f"   {i}. \"{msg}\"")
    
    print(f"\n   → Emotion: {result3['primary_emotion']}")
    print(f"   → Confidence: {result3['confidence']:.3f}")
    print(f"   → Source: {result3['source']}")
    
    print("\n" + "="*80)
    print("💡 ROOT CAUSE IDENTIFIED")
    print("="*80)
    print("""
The issue is in chat.py line 175:
    recent_user_msgs = [msg["content"] for msg in chat_history if msg["role"] == "user"][-5:]
    recent_user_msgs.append(message_req.content)
    emotion_data = emotion_service.detect_contextual_emotion(recent_user_msgs)

When you send "Hello", it analyzes it WITH context of your previous emotional
messages about project anxiety/fear. The ML model sees the COMBINED context and
detects the overall emotional tone (fear/anger), not just the "Hello".

SOLUTIONS:
1. Weight the most recent message more heavily
2. For short greetings (< 10 chars), analyze WITHOUT context
3. Use a time-based context window (ignore messages > 5 min old)
4. Implement message importance scoring
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_context_issue())
