"""Test chatbot API endpoint directly with HTTP request."""
import requests
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Get auth token
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")  # Use SUPABASE_KEY not SUPABASE_ANON_KEY

print("=" * 80)
print("TESTING CHATBOT API ENDPOINT")
print("=" * 80)

# Login to get auth token
print("\n1. Logging in to get auth token...")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

try:
    # Use test user credentials
    auth_response = supabase.auth.sign_in_with_password({
        "email": "1by23is227@bmsit.in",
        "password": "testuser123"
    })
    
    token = auth_response.session.access_token
    user_id = auth_response.user.id
    print(f"✅ Logged in as: {auth_response.user.email}")
    print(f"   User ID: {user_id}")
    print(f"   Token: {token[:50]}...")
except Exception as e:
    print(f"❌ Login failed: {e}")
    import sys
    sys.exit(1)

# Test chatbot endpoint
print("\n2. Testing /api/v1/chat/message endpoint...")
url = "http://localhost:8000/api/v1/chat/message"

payload = {
    "content": "Hello! I'm feeling stressed. Can you help?"
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"   Session ID: {data.get('session_id')}")
        print(f"   Response: {data.get('response', '')[:200]}...")
        print(f"   Emotion: {data.get('emotion_detected')}")
        print(f"   Crisis: {data.get('crisis_detected')}")
    else:
        print(f"\n❌ FAILED")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR: Backend server is not running!")
    print("   Please start the backend server with:")
    print("   cd backend && python -m uvicorn app.main:app --reload")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
