"""Test Gemini API connectivity and response."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_chatbot import get_chatbot
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("\n" + "="*80)
print("🧪 TESTING GEMINI CHATBOT CONNECTIVITY")
print("="*80)

# Get chatbot instance
chatbot = get_chatbot()

print(f"\n1. Chatbot Initialization:")
print(f"   - Is Available: {chatbot.is_available()}")
print(f"   - Has Model: {chatbot.model is not None}")
print(f"   - API Key: {'***' + chatbot.api_key[-10:] if chatbot.api_key else 'NOT SET'}")

if not chatbot.is_available():
    print(f"\n❌ CHATBOT NOT AVAILABLE")
    print(f"   - Check GEMINI_API_KEY in config.py")
    print(f"   - Current key: {chatbot.api_key[:20] if chatbot.api_key else 'None'}...")
    exit(1)

# Test simple message
print(f"\n2. Testing Simple Message:")
test_message = "Hello, how are you?"
print(f"   Message: \"{test_message}\"")

try:
    response = chatbot.chat(test_message)
    print(f"\n✅ Response received ({len(response)} chars):")
    print(f"   {response[:200]}...")
    
    if "unable to connect" in response.lower() or "fallback" in response.lower():
        print(f"\n⚠️  WARNING: Got fallback response!")
        print(f"   Full response: {response}")
    else:
        print(f"\n✅ Got real Gemini response (not fallback)")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test with history
print(f"\n3. Testing With Chat History:")
history = [
    {"role": "user", "content": "I'm feeling anxious"},
    {"role": "assistant", "content": "I understand. Let's try some breathing exercises."}
]

test_message_2 = "What breathing exercise do you recommend?"
print(f"   Message: \"{test_message_2}\"")
print(f"   History: {len(history)} messages")

try:
    response2 = chatbot.chat(test_message_2, history)
    print(f"\n✅ Response received ({len(response2)} chars):")
    print(f"   {response2[:200]}...")
    
    if "unable to connect" in response2.lower() or "fallback" in response2.lower():
        print(f"\n⚠️  WARNING: Got fallback response!")
    else:
        print(f"\n✅ Got real Gemini response with context")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("📋 DIAGNOSIS")
print("="*80)
print("""
If you see "Got real Gemini response" → Gemini is working fine
If you see "Got fallback response" → There's an issue with Gemini API

Common issues:
1. API Key invalid or expired
2. API quota exceeded
3. Network connectivity issues
4. Gemini service temporarily down
5. Safety filters blocking content
""")
print("="*80 + "\n")
