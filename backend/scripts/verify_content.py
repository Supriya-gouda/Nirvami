import requests
import sys
import os
from supabase import create_client
from dotenv import load_dotenv

# Load env vars for direct DB check
load_dotenv("backend/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def verify_api_content():
    print("\n🔍 Verifying API Content...")
    
    # 1. Check Yoga Poses
    try:
        # We need a user token for the API, but for now let's see if we can check DB directly 
        # or if we can use the debug endpoint approach.
        # Actually, the API requires authentication.
        # I'll skip API check for now and check DB directly for all content to be sure.
        pass
    except Exception as e:
        print(f"API Check skipped: {e}")

def verify_db_content():
    print("\n🔍 Verifying Database Content...")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials in environment")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 1. Check Yoga Poses
    try:
        response = supabase.table("yoga_poses").select("count", count="exact").execute()
        count = response.count
        print(f"🧘 Yoga Poses: {count}")
        if count == 0:
            print("❌ No yoga poses found!")
        else:
            print("✅ Yoga poses present")
    except Exception as e:
        print(f"❌ Error checking yoga poses: {e}")

    # 2. Check Sound Tracks
    try:
        response = supabase.table("sound_tracks").select("count", count="exact").execute()
        count = response.count
        print(f"🎵 Sound Tracks: {count}")
        if count == 0:
            print("❌ No sound tracks found!")
        else:
            print("✅ Sound tracks present")
    except Exception as e:
        print(f"❌ Error checking sound tracks: {e}")

    # 3. Check Ayurveda Resources
    try:
        response = supabase.table("ayurveda_resources").select("count", count="exact").execute()
        count = response.count
        print(f"📚 Ayurveda Resources: {count}")
        if count == 0:
            print("❌ No ayurveda resources found!")
        else:
            print("✅ Ayurveda resources present")
    except Exception as e:
        print(f"❌ Error checking ayurveda resources: {e}")

if __name__ == "__main__":
    verify_db_content()
