"""Test script to verify practice API endpoints."""
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def test_practice_content():
    """Test fetching practice content."""
    print("🧪 Testing Practice API...")
    print("-" * 50)
    
    # Use service role key to bypass RLS for testing
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    try:
        # Test 1: Fetch all practice content
        print("\n1️⃣ Fetching all practice content...")
        result = supabase.table("practice_content").select("*").execute()
        
        if result.data:
            print(f"   ✅ Found {len(result.data)} practices")
            for practice in result.data[:3]:  # Show first 3
                print(f"      • {practice['practice_name']} ({practice['practice_type']})")
        else:
            print("   ❌ No practice content found")
            return False
        
        # Test 2: Fetch specific practice
        print("\n2️⃣ Fetching specific practice: Child's Pose...")
        result = supabase.table("practice_content").select("*").eq("practice_name", "Child's Pose").execute()
        
        if result.data and len(result.data) > 0:
            practice = result.data[0]
            print(f"   ✅ Found practice: {practice['practice_name']}")
            print(f"      • Type: {practice['practice_type']}")
            print(f"      • Difficulty: {practice['difficulty']}")
            print(f"      • Duration: {practice['duration_min']}-{practice['duration_max']} min")
            print(f"      • YouTube: {practice['youtube_video_id']}")
            print(f"      • TTS Instructions: {len(practice.get('tts_instructions', []))} steps")
        else:
            print("   ❌ Practice not found")
            return False
        
        # Test 3: Check practice_sessions table exists
        print("\n3️⃣ Checking practice_sessions table...")
        result = supabase.table("practice_sessions").select("id").limit(1).execute()
        print(f"   ✅ practice_sessions table accessible")
        
        # Test 4: Check practice_streaks table exists
        print("\n4️⃣ Checking practice_streaks table...")
        result = supabase.table("practice_streaks").select("id").limit(1).execute()
        print(f"   ✅ practice_streaks table accessible")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_practice_content())
