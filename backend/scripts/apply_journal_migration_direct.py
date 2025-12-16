"""
Apply journal migration SQL statements one by one.
Executes each statement separately to handle errors better.
"""
import os
from supabase import create_client
from pathlib import Path

# Configuration
SUPABASE_URL = "https://pmanclxqnmihwiwntadt.supabase.co"
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_SERVICE_KEY:
    print("❌ Error: SUPABASE_SERVICE_KEY environment variable not set")
    exit(1)

# Initialize Supabase client with service role (bypasses RLS)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Read SQL file
script_dir = Path(__file__).parent.absolute()
sql_file = script_dir / ".." / "database" / "apply_journal_migration.sql"

print(f"📖 Reading SQL from: {sql_file}")

with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

print(f"✅ SQL file read successfully ({len(sql_content)} characters)")
print("\n" + "="*60)
print("IMPORTANT: Manual SQL Execution Required")
print("="*60)
print("\nSupabase Python client doesn't support raw SQL execution.")
print("Please follow these steps:\n")
print("1. Open Supabase SQL Editor:")
print("   https://supabase.com/dashboard/project/pmanclxqnmihwiwntadt/editor\n")
print("2. Copy the SQL below")
print("3. Paste it into the SQL Editor")
print("4. Click 'Run' to execute\n")
print("="*60)
print("\nSQL TO EXECUTE:\n")
print(sql_content)
print("\n" + "="*60)
print("\n✅ After running the SQL, test the journal feature!")
