"""Test inserting a wearable snapshot directly."""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

USER_ID = "c61e78d5-f0b4-475a-a41c-d605a0616d49"

def test_snapshot_insert():
    """Test inserting a snapshot with service role."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    admin_client = create_client(supabase_url, service_key)
    
    # Create a test snapshot
    test_snapshot = {
        'user_id': USER_ID,
        'provider': 'apple_watch',
        'captured_at': '2025-11-24T12:00:00Z',
        'recorded_at': '2025-11-24T12:00:00Z',  # Required field
        'source': 'watch',
        'heart_rate': 75,
        'steps': 5000,
        'sleep_hours': 7.5,
        'calories_burned': 400
    }
    
    print("=" * 80)
    print("TESTING SNAPSHOT INSERT")
    print("=" * 80)
    print(f"\nUser ID: {USER_ID}")
    print(f"Snapshot: {test_snapshot}")
    print("\n1. Checking if profile exists...")
    
    # Check profile
    profile_check = admin_client.table('profiles').select('id,email').eq('id', USER_ID).execute()
    
    if profile_check.data:
        print(f"✅ Profile exists: {profile_check.data[0].get('email')}")
    else:
        print("❌ Profile does not exist!")
        return
    
    print("\n2. Attempting to insert snapshot...")
    
    try:
        result = admin_client.table('wearable_snapshots').insert(test_snapshot).execute()
        
        if result.data:
            print(f"✅ SUCCESS! Inserted snapshot:")
            print(f"   ID: {result.data[0].get('id')}")
            print(f"   Time: {result.data[0].get('captured_at')}")
            print(f"   Heart Rate: {result.data[0].get('heart_rate')}")
            print(f"   Steps: {result.data[0].get('steps')}")
            
            # Clean up
            print("\n3. Cleaning up test data...")
            admin_client.table('wearable_snapshots').delete().eq('id', result.data[0]['id']).execute()
            print("✅ Test snapshot deleted")
        else:
            print("❌ FAILED! No data returned from insert")
            
    except Exception as e:
        print(f"❌ ERROR inserting snapshot: {e}")
        print(f"   Error type: {type(e).__name__}")
        if hasattr(e, 'message'):
            print(f"   Message: {e.message}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_snapshot_insert()
