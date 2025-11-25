"""Test Gemini chatbot directly to diagnose issues."""
import os
import sys
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.services.gemini_chatbot import get_chatbot

print("=" * 80)
print("TESTING GEMINI CHATBOT")
print("=" * 80)

chatbot = get_chatbot()

print(f"\n1. Chatbot available: {chatbot.is_available()}")
print(f"2. API Key configured: {'Yes' if chatbot.api_key else 'No'}")
print(f"3. Model initialized: {'Yes' if chatbot.model else 'No'}")

if not chatbot.is_available():
    print("\n❌ Chatbot is NOT available. Check:")
    print("   - GEMINI_API_KEY in .env file")
    print("   - google-generativeai package installed")
    print("   - API key is valid")
    sys.exit(1)

print("\n4. Testing simple message...")
try:
    response = chatbot.chat("Hello, can you hear me? Just say 'Yes, I can hear you.'")
    print(f"✅ Response received: {response[:200]}")
    print(f"   Length: {len(response)} characters")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(2)

print("\n5. Testing with mental health question...")
try:
    response = chatbot.chat("I'm feeling stressed. What breathing exercise can help?")
    print(f"✅ Response received: {response[:300]}...")
    print(f"   Length: {len(response)} characters")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(3)

print("\n" + "=" * 80)
print("✅ CHATBOT IS WORKING CORRECTLY")
print("=" * 80)
