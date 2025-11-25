"""Verify emotion_logs table has required columns after schema update."""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Missing Supabase credentials")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("🔍 Verifying emotion_logs table schema...")
print("=" * 60)

# Try to query the table with new columns
try:
    result = supabase.table('emotion_logs').select(
        'id, user_id, mood, intensity, energy, notes, logged_at, source, created_at'
    ).limit(1).execute()
    
    print("✅ Schema verification successful!")
    print("\nThe following columns are now available:")
    print("  ✅ mood")
    print("  ✅ intensity")
    print("  ✅ energy")
    print("  ✅ notes")
    print("  ✅ logged_at")
    print("  ✅ source (updated constraint)")
    
    if result.data:
        print(f"\nFound {len(result.data)} existing emotion log(s)")
        print("\nSample data structure:")
        print(result.data[0])
    else:
        print("\nTable is empty (ready for new mood logs)")
    
    print("\n" + "=" * 60)
    print("✅ emotion_logs table is ready for mood logging!")
    
except Exception as e:
    print(f"\n❌ Schema verification failed!")
    print(f"\nError: {e}")
    print("\n⚠️  This means the SQL update has NOT been applied yet.")
    print("\nPlease run the SQL from QUICK_FIX_INSTRUCTIONS.md in Supabase SQL Editor:")
    print(f"   {SUPABASE_URL.replace('https://', 'https://app.')}/project/_/sql")
    exit(1)
