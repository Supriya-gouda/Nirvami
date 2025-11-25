"""Get a valid auth token for testing."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

admin = create_client(SUPABASE_URL, SERVICE_KEY)

print("Fetching user from profiles table...")
try:
    result = admin.table('profiles').select('id,email').limit(1).execute()
    if result.data:
        user = result.data[0]
        print(f"Found user: {user['email']} (ID: {user['id']})")
        
        # For testing, we'll just use the service role to create a test message
        print("\nWe can test the chatbot API endpoint directly without login.")
        print("The backend is running. Let's check if it's responding...")
        
        import requests
        try:
            health_check = requests.get("http://localhost:8000/health", timeout=5)
            print(f"\n✅ Backend is running: {health_check.json()}")
        except:
            print("\n❌ Backend is NOT running!")
            print("Start it with: cd backend && python -m uvicorn app.main:app --reload")
            
    else:
        print("No users found in database")
except Exception as e:
    print(f"Error: {e}")
