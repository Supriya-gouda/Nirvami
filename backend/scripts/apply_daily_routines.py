"""
Apply Daily Routines table to Supabase database.
Run this script to add the daily_routines table for Ayurvedic dinacharya tracking.
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
    sys.exit(1)

# Read migration SQL
migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'daily_routines_migration.sql')
with open(migration_path, 'r') as f:
    migration_sql = f.read()

print("🚀 Connecting to Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("📝 Applying daily_routines table migration...")
try:
    # Execute migration
    result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
    print("✅ Migration applied successfully!")
    
    # Verify table exists
    print("\n🔍 Verifying table structure...")
    verify_result = supabase.table('daily_routines').select('*').limit(1).execute()
    print("✅ Table 'daily_routines' verified and ready!")
    
    print("\n✨ Migration complete! You can now:")
    print("   - Add daily routine entries via POST /routines/entry")
    print("   - View routines via GET /routines/entries")
    print("   - Delete routines via DELETE /routines/entry/{id}")
    
except Exception as e:
    print(f"❌ Migration failed: {str(e)}")
    print("\n💡 You may need to run the SQL manually in Supabase SQL Editor:")
    print("   1. Go to Supabase Dashboard > SQL Editor")
    print("   2. Paste contents of backend/database/daily_routines_migration.sql")
    print("   3. Click 'Run'")
    sys.exit(1)
