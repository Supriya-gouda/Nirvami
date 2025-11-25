"""Apply emotion_logs schema update to Supabase."""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Missing Supabase credentials in .env file")
    print("   Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Read SQL file
with open('backend/database/update_emotion_logs_schema.sql', 'r') as f:
    sql_statements = f.read()

print("📝 Applying emotion_logs schema update...")
print("=" * 60)

try:
    # Execute SQL via Supabase RPC (you may need to run this manually in Supabase SQL editor)
    print("\nSQL to execute:")
    print("-" * 60)
    print(sql_statements)
    print("-" * 60)
    print("\n✅ Please copy the above SQL and run it in Supabase SQL Editor:")
    print(f"   {SUPABASE_URL.replace('https://', 'https://app.')}/project/_/sql")
    print("\nThis will add the following columns to emotion_logs:")
    print("   - mood TEXT")
    print("   - intensity INTEGER (1-10)")
    print("   - energy INTEGER (1-10)")
    print("   - notes TEXT")
    print("   - logged_at TIMESTAMPTZ")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
