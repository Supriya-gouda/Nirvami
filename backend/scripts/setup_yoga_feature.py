"""
Apply yoga and sound therapy schema, then seed data.
Run this script to set up the complete yoga/sound therapy feature.
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🚀 Setting up Yoga & Sound Therapy feature...")
print("=" * 60)

# Read and execute schema SQL
print("\n📋 Applying database schema...")
try:
    with open('../database/yoga_sound_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Note: Supabase Python client doesn't support raw SQL execution
    # You need to run this in Supabase SQL Editor manually
    print("⚠️  Please run the SQL from 'backend/database/yoga_sound_schema.sql'")
    print("   in your Supabase SQL Editor: https://supabase.com/dashboard")
    print("\nAfter running the SQL, press Enter to continue with data seeding...")
    input()
    
except Exception as e:
    print(f"❌ Error reading schema: {e}")
    exit(1)

# Now run the seeding script
print("\n📥 Seeding data...")
exec(open('seed_yoga_content.py').read())

print("\n✅ Setup complete!")
