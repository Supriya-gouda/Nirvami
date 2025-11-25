"""Get actual columns from database."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_columns():
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    admin_client = create_client(supabase_url, service_key)
    
    # Insert a test row with minimal data to see what columns exist
    test_row = {
        'user_id': 'c61e78d5-f0b4-475a-a41c-d605a0616d49',
        'recorded_at': '2025-11-24T12:00:00Z',
        'device_type': 'manual_form',
        'heart_rate': 75
    }
    
    print("Testing with old schema (device_type, recorded_at)...")
    try:
        result = admin_client.table('wearable_snapshots').insert(test_row).execute()
        if result.data:
            print(f"✅ SUCCESS with old schema!")
            print(f"   Columns in result: {list(result.data[0].keys())}")
            # Delete it
            admin_client.table('wearable_snapshots').delete().eq('id', result.data[0]['id']).execute()
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    get_columns()
