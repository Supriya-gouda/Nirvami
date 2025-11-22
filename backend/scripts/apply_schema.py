"""Apply database schema to Supabase."""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from supabase import create_client


def load_schema():
    """Load schema SQL file."""
    schema_path = backend_dir / "database" / "schema.sql"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return f.read()


def apply_schema():
    """Apply schema to Supabase database."""
    print("="*50)
    print("🗄️  SUPABASE SCHEMA APPLICATION")
    print("="*50)
    
    print(f"\n📍 Target: {settings.SUPABASE_URL}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    
    # Load schema
    print("\n📖 Loading schema file...")
    schema_sql = load_schema()
    print(f"   ✅ Loaded {len(schema_sql)} characters")
    
    # Create Supabase client with service role key
    print("\n🔌 Connecting to Supabase...")
    try:
        # Note: We need to use the REST API or psql to run SQL
        # The Supabase Python client doesn't support arbitrary SQL execution
        print("   ℹ️  Please use one of these methods:")
        print("\n   METHOD 1: Supabase SQL Editor (Recommended)")
        print("   ------------------------------------------")
        print("   1. Go to https://app.supabase.com")
        print("   2. Open your project")
        print("   3. Click 'SQL Editor' in sidebar")
        print("   4. Click 'New query'")
        print("   5. Copy contents of backend/database/schema.sql")
        print("   6. Paste and click 'Run'")
        
        print("\n   METHOD 2: psql Command Line")
        print("   ---------------------------")
        print("   Get your connection string from Supabase Settings > Database")
        print("   Then run:")
        print(f"   psql \"postgresql://postgres:[PASSWORD]@db.*.supabase.co:5432/postgres\" \\")
        print(f"        -f {backend_dir / 'database' / 'schema.sql'}")
        
        print("\n   METHOD 3: Copy SQL Below")
        print("   ------------------------")
        print("   The schema SQL is ready to copy:")
        schema_file = backend_dir / 'database' / 'schema.sql'
        print(f"   File: {schema_file}")
        
        # Ask if user wants to see the SQL
        response = input("\n   Show SQL? (y/n): ").strip().lower()
        if response == 'y':
            print("\n" + "="*50)
            print(schema_sql)
            print("="*50)
        
        print("\n✅ After running the schema, verify with:")
        print("   python backend/scripts/test_database.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    apply_schema()
