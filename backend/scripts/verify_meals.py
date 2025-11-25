import requests
import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load env vars
load_dotenv("backend/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get a valid JWT for testing."""
    print("  🔐 Authenticating test user...")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  ❌ Missing Supabase credentials")
        sys.exit(1)
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # List existing users
    try:
        print("  📋 Listing users...")
        users = supabase.auth.admin.list_users()
        if users:
            print(f"  Found {len(users)} users.")
            for u in users[:3]:
                print(f"    - {u.email} ({u.id})")
        else:
            print("  No users found.")
    except Exception as e:
        print(f"  ⚠️  Failed to list users: {e}")

    email = "testuser@example.com"
    password = "TestPassword123!"
    
    try:
        # Try to sign in
        print(f"  🔑 Signing in as {email}...")
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res.session.access_token, res.user.id
    except Exception as e:
        print(f"  ⚠️  Sign in failed: {e}")
        try:
            # Create user if not exists
            print("  👤 Creating test user...")
            attributes = {
                "email": email, 
                "password": password, 
                "email_confirm": True,
                "user_metadata": {"name": "Test User"}
            }
            user = supabase.auth.admin.create_user(attributes)
            print(f"  ✅ User created: {user.user.id}")
            
            # Now sign in
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            return res.session.access_token, res.user.id
        except Exception as e:
            print(f"  ❌ Auth failed: {e}")
            # Fallback: Try to use the test user ID if we can't auth (but RLS will fail)
            return None, None

def verify_meals():
    print("\n🥗 Verifying Meal Tracking...")
    
    token, user_id = get_auth_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print(f"  ✅ Authenticated as {user_id}")
    else:
        print("  ⚠️  Proceeding without auth (RLS may fail)")
    
    # 1. Create a Meal
    print("  Creating a test meal...")
    meal_data = {
        "meal_time": datetime.now().isoformat(),
        "meal_type": "breakfast",
        "meal_text": "Oatmeal with blueberries and almonds",
        "ingredients": ["oats", "blueberries", "almonds", "honey"],
        "calories": 350,
        "dosha_impact_tags": {"kapha": "balancing", "vata": "grounding"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/meals/log", json=meal_data, headers=headers)
        
        if response.status_code == 200:
            created_meal = response.json()
            print(f"  ✅ Meal created: {created_meal.get('id')}")
            
            # 2. Get Meal History
            print("  Fetching meal history...")
            history_response = requests.get(f"{BASE_URL}/meals/history", headers=headers)
            
            if history_response.status_code == 200:
                meals = history_response.json()
                print(f"  ✅ Retrieved {len(meals)} meals")
                
                # Verify our meal is there
                found = any(m['id'] == created_meal['id'] for m in meals)
                if found:
                    print("  ✅ Verification Successful: Created meal found in history")
                else:
                    print("  ❌ Verification Failed: Created meal NOT found in history")
                    sys.exit(1)
            else:
                print(f"  ❌ Failed to get history: {history_response.text}")
                sys.exit(1)
                
        else:
            print(f"  ❌ Failed to create meal: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_meals()
