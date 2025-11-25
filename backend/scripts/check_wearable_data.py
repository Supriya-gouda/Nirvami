"""Check if wearable data exists in database."""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

USER_ID = "c61e78d5-f0b4-475a-a41c-d605a0616d49"

def check_data():
    """Check wearable data in database."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    admin_client = create_client(supabase_url, service_key)
    
    print("=" * 80)
    print("CHECKING WEARABLE DATA IN DATABASE")
    print("=" * 80)
    print(f"\nUser ID: {USER_ID}\n")
    
    # Check wearable_snapshots
    print("1. Checking wearable_snapshots table...")
    snapshots = admin_client.table('wearable_snapshots').select('*').eq('user_id', USER_ID).order('created_at', desc=True).limit(10).execute()
    
    if snapshots.data:
        print(f"   ✅ Found {len(snapshots.data)} snapshots")
        for i, s in enumerate(snapshots.data, 1):
            print(f"   {i}. Source: {s.get('source'):8} | Date: {s.get('captured_at')[:10]} | HR: {s.get('heart_rate'):3} | Steps: {s.get('steps'):5} | Sleep: {s.get('sleep_hours')}")
    else:
        print("   ❌ No snapshots found")
    
    # Check wearable_daily_stats
    print("\n2. Checking wearable_daily_stats table...")
    daily_stats = admin_client.table('wearable_daily_stats').select('*').eq('user_id', USER_ID).order('date', desc=True).limit(10).execute()
    
    if daily_stats.data:
        print(f"   ✅ Found {len(daily_stats.data)} daily stats")
        for i, s in enumerate(daily_stats.data, 1):
            print(f"   {i}. Date: {s.get('date')} | Avg HR: {s.get('avg_heart_rate'):3} | Steps: {s.get('total_steps'):5} | Sleep: {s.get('sleep_hours')}")
    else:
        print("   ❌ No daily stats found")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_data()
