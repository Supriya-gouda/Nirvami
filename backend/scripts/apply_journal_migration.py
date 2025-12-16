"""
Apply Journal Migration to Supabase Database
"""
import os
from supabase import create_client

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://pmanclxqnmihwiwntadt.supabase.co')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Need service role key for DDL

if not SUPABASE_SERVICE_KEY:
    print("❌ Error: SUPABASE_SERVICE_KEY environment variable not set")
    print("\nTo apply this migration:")
    print("1. Go to https://supabase.com/dashboard/project/pmanclxqnmihwiwntadt/settings/api")
    print("2. Copy your 'service_role' key (NOT the anon key)")
    print("3. Set it as environment variable: $env:SUPABASE_SERVICE_KEY='your-key-here'")
    print("4. Run this script again")
    print("\nOR")
    print("\n5. Manually run the SQL in Supabase SQL Editor:")
    print("   - Open: https://supabase.com/dashboard/project/pmanclxqnmihwiwntadt/editor")
    print("   - Copy contents of: backend/database/apply_journal_migration.sql")
    print("   - Paste and run in SQL Editor")
    exit(1)

# Read migration file
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
migration_path = os.path.join(script_dir, '..', 'database', 'apply_journal_migration.sql')

with open(migration_path, 'r') as f:
    migration_sql = f.read()

print("🔄 Connecting to Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("🔄 Applying journal migration...")
try:
    # Execute SQL using Supabase REST API
    result = supabase.rpc('exec_sql', {'query': migration_sql}).execute()
    print("✅ Migration applied successfully!")
    print("\n📊 Tables created:")
    print("   - journal_entries (with emotion columns)")
    print("   - journal_insights")
    print("\n🔒 RLS policies created")
    print("📇 Indexes created")
    print("\n✅ Journal feature is ready to use!")
except Exception as e:
    print(f"❌ Error applying migration: {e}")
    print("\nPlease apply the migration manually:")
    print("1. Open: https://supabase.com/dashboard/project/pmanclxqnmihwiwntadt/editor")
    print("2. Copy contents of: backend/database/apply_journal_migration.sql")
    print("3. Paste and run in SQL Editor")
