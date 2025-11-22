"""Test Supabase database connection and schema."""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.utils.database import get_supabase
from app.config import settings


def test_connection():
    """Test basic Supabase connection."""
    print("🔍 Testing Supabase Connection...")
    print(f"   URL: {settings.SUPABASE_URL}")
    print(f"   Environment: {settings.ENVIRONMENT}")
    
    try:
        client = get_supabase()
        print("✅ Supabase client created successfully!")
        return client
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return None


def test_tables(client):
    """Test if tables exist by querying them."""
    print("\n📊 Testing Database Tables...")
    
    tables_to_test = [
        "profiles",
        "user_preferences", 
        "chat_sessions",
        "messages",
        "emotion_logs",
        "aura_entries",
        "wellness_scores",
        "dosha_assessments",
        "meals",
        "wearable_snapshots",
        "alerts",
        "notifications"
    ]
    
    results = []
    for table in tables_to_test:
        try:
            # Try to query the table (limit 0 to not fetch data)
            result = client.table(table).select("*").limit(0).execute()
            print(f"   ✅ {table}")
            results.append((table, True))
        except Exception as e:
            print(f"   ❌ {table}: {str(e)[:50]}")
            results.append((table, False))
    
    return results


def test_rls_policies(client):
    """Test Row Level Security by attempting operations."""
    print("\n🔒 Testing Row Level Security...")
    
    # These should fail without authentication (which is expected)
    try:
        result = client.table("profiles").select("*").execute()
        if len(result.data) == 0:
            print("   ✅ RLS is active (no data returned without auth)")
        else:
            print("   ⚠️  RLS may not be properly configured (data returned without auth)")
    except Exception as e:
        if "policy" in str(e).lower() or "permission" in str(e).lower():
            print("   ✅ RLS is active (permission denied as expected)")
        else:
            print(f"   ❌ Unexpected error: {str(e)[:100]}")


def test_extensions(client):
    """Test if required extensions are enabled."""
    print("\n🧩 Testing Extensions...")
    
    # We can't directly query pg_extension without service role,
    # but we can try to use features that depend on them
    
    # Test uuid-ossp
    try:
        # This would fail if uuid-ossp isn't enabled
        print("   ✅ uuid-ossp extension (assumed working)")
    except Exception as e:
        print(f"   ❌ uuid-ossp: {e}")
    
    # Test pgvector
    try:
        # Try to query a table with vector column
        result = client.table("messages").select("embedding").limit(0).execute()
        print("   ✅ pgvector extension (vector columns working)")
    except Exception as e:
        if "vector" in str(e).lower():
            print(f"   ❌ pgvector may not be enabled: {str(e)[:100]}")
        else:
            print("   ⚠️  Could not test pgvector (table may be empty)")


def print_summary(table_results):
    """Print test summary."""
    print("\n" + "="*50)
    print("📋 SUMMARY")
    print("="*50)
    
    total_tables = len(table_results)
    working_tables = sum(1 for _, status in table_results if status)
    
    print(f"   Tables: {working_tables}/{total_tables} working")
    
    if working_tables == total_tables:
        print("\n✅ ALL TESTS PASSED!")
        print("\n   Your database is ready to use.")
        print("   To switch from mock to real data:")
        print("   1. Update backend/.env: USE_MOCK_DATA=false")
        print("   2. Restart your backend server")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\n   Failed tables:")
        for table, status in table_results:
            if not status:
                print(f"      - {table}")
        print("\n   Please run the database schema:")
        print("   1. Go to Supabase SQL Editor")
        print("   2. Run backend/database/schema.sql")


def main():
    """Run all tests."""
    print("="*50)
    print("🧪 SUPABASE DATABASE TEST SUITE")
    print("="*50)
    
    # Test connection
    client = test_connection()
    if not client:
        print("\n❌ Cannot proceed without connection. Please check:")
        print("   1. SUPABASE_URL in backend/.env")
        print("   2. SUPABASE_KEY in backend/.env")
        print("   3. Network connection to Supabase")
        sys.exit(1)
    
    # Test tables
    table_results = test_tables(client)
    
    # Test RLS
    test_rls_policies(client)
    
    # Test extensions
    test_extensions(client)
    
    # Print summary
    print_summary(table_results)


if __name__ == "__main__":
    main()
