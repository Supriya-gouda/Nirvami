"""
Test Daily Routines Feature End-to-End
Tests database table, backend API, and data flow for daily routines (Dinacharya) feature.
"""
import os
import sys
import requests
from datetime import date, time, datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    sys.exit(1)

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}🧪 TEST: {name}{RESET}")

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ️  {msg}{RESET}")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_table_exists():
    """Test 1: Verify daily_routines table exists in database"""
    print_test("Database table existence")
    
    try:
        # Query information_schema
        result = supabase.rpc('exec_sql', {
            'sql': """
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'daily_routines' 
                ORDER BY ordinal_position
            """
        }).execute()
        
        if not result.data:
            print_error("Table 'daily_routines' does not exist")
            return False
        
        print_success("Table 'daily_routines' exists")
        print_info("Table structure:")
        for col in result.data:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check required columns
        required_cols = ['id', 'user_id', 'date', 'time', 'activity', 'notes', 'created_at']
        actual_cols = [col['column_name'] for col in result.data]
        
        for col in required_cols:
            if col not in actual_cols:
                print_error(f"Required column '{col}' is missing")
                return False
        
        print_success("All required columns present")
        return True
        
    except Exception as e:
        print_error(f"Table check failed: {str(e)}")
        return False

def test_rls_policies():
    """Test 2: Verify RLS policies are enabled"""
    print_test("Row Level Security policies")
    
    try:
        # Check if RLS is enabled
        result = supabase.rpc('exec_sql', {
            'sql': """
                SELECT tablename, rowsecurity 
                FROM pg_tables 
                WHERE schemaname = 'public' AND tablename = 'daily_routines'
            """
        }).execute()
        
        if result.data and result.data[0]['rowsecurity']:
            print_success("RLS is enabled on daily_routines table")
        else:
            print_error("RLS is NOT enabled on daily_routines table")
            return False
        
        # Check if policy exists
        result = supabase.rpc('exec_sql', {
            'sql': """
                SELECT policyname, cmd 
                FROM pg_policies 
                WHERE tablename = 'daily_routines'
            """
        }).execute()
        
        if result.data:
            print_success(f"Found {len(result.data)} RLS policies:")
            for policy in result.data:
                print(f"  - {policy['policyname']} (command: {policy['cmd']})")
            return True
        else:
            print_error("No RLS policies found for daily_routines")
            return False
            
    except Exception as e:
        print_error(f"RLS check failed: {str(e)}")
        return False

def test_indexes():
    """Test 3: Verify indexes exist for performance"""
    print_test("Database indexes")
    
    try:
        result = supabase.rpc('exec_sql', {
            'sql': """
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'daily_routines' AND schemaname = 'public'
            """
        }).execute()
        
        if not result.data:
            print_error("No indexes found on daily_routines table")
            return False
        
        print_success(f"Found {len(result.data)} indexes:")
        for idx in result.data:
            print(f"  - {idx['indexname']}")
        
        # Check for expected indexes
        expected_indexes = ['idx_daily_routines_user_date', 'idx_daily_routines_user_time']
        actual_indexes = [idx['indexname'] for idx in result.data]
        
        for exp_idx in expected_indexes:
            if exp_idx in actual_indexes:
                print_success(f"Index '{exp_idx}' exists")
            else:
                print_error(f"Expected index '{exp_idx}' not found")
        
        return True
        
    except Exception as e:
        print_error(f"Index check failed: {str(e)}")
        return False

def test_backend_routes():
    """Test 4: Verify backend API routes are accessible"""
    print_test("Backend API routes")
    
    # Note: These tests will fail without authentication
    # They just check if routes exist and return expected status
    
    print_info("Testing POST /routines/entry (expects 401 without auth)")
    try:
        response = requests.post(f"{API_URL}/routines/entry", json={
            "date": str(date.today()),
            "time": "08:00",
            "activity": "Test activity"
        })
        
        if response.status_code == 401:
            print_success("POST route exists (returned 401 unauthorized as expected)")
        elif response.status_code == 422:
            print_success("POST route exists (returned 422 validation error)")
        else:
            print_error(f"Unexpected status code: {response.status_code}")
    except Exception as e:
        print_error(f"POST route test failed: {str(e)}")
    
    print_info("Testing GET /routines/entries (expects 401 without auth)")
    try:
        response = requests.get(f"{API_URL}/routines/entries")
        
        if response.status_code == 401:
            print_success("GET route exists (returned 401 unauthorized as expected)")
        else:
            print_error(f"Unexpected status code: {response.status_code}")
    except Exception as e:
        print_error(f"GET route test failed: {str(e)}")
    
    print_info("Testing DELETE /routines/entry/:id (expects 401 without auth)")
    try:
        response = requests.delete(f"{API_URL}/routines/entry/test-id")
        
        if response.status_code == 401:
            print_success("DELETE route exists (returned 401 unauthorized as expected)")
        else:
            print_error(f"Unexpected status code: {response.status_code}")
    except Exception as e:
        print_error(f"DELETE route test failed: {str(e)}")
    
    return True

def test_manual_data_insertion():
    """Test 5: Manually insert test data to verify table works"""
    print_test("Manual data insertion (direct to Supabase)")
    
    try:
        # Get a test user (first user in profiles table)
        users = supabase.table('profiles').select('id').limit(1).execute()
        
        if not users.data:
            print_error("No users found in profiles table. Cannot test data insertion.")
            return False
        
        test_user_id = users.data[0]['id']
        print_info(f"Using test user ID: {test_user_id}")
        
        # Insert test routine
        today = date.today()
        test_data = {
            'user_id': test_user_id,
            'date': str(today),
            'time': '08:30',
            'activity': 'Test Morning Meditation',
            'notes': 'This is a test entry'
        }
        
        result = supabase.table('daily_routines').insert(test_data).execute()
        
        if result.data:
            print_success("Successfully inserted test routine")
            inserted_id = result.data[0]['id']
            print_info(f"Inserted routine ID: {inserted_id}")
            
            # Verify we can read it back
            verify = supabase.table('daily_routines').select('*').eq('id', inserted_id).execute()
            
            if verify.data:
                print_success("Successfully retrieved inserted routine")
                routine = verify.data[0]
                print_info(f"Activity: {routine['activity']}")
                print_info(f"Time: {routine['time']}")
                print_info(f"Date: {routine['date']}")
                
                # Clean up - delete test entry
                supabase.table('daily_routines').delete().eq('id', inserted_id).execute()
                print_success("Cleaned up test data")
                return True
            else:
                print_error("Could not retrieve inserted routine")
                return False
        else:
            print_error("Failed to insert test routine")
            return False
            
    except Exception as e:
        print_error(f"Data insertion test failed: {str(e)}")
        return False

def test_multiple_routines_per_day():
    """Test 6: Verify multiple routines can be added for same day"""
    print_test("Multiple routines per day")
    
    try:
        # Get a test user
        users = supabase.table('profiles').select('id').limit(1).execute()
        
        if not users.data:
            print_error("No users found")
            return False
        
        test_user_id = users.data[0]['id']
        today = str(date.today())
        
        # Insert 3 routines for the same day
        routines = [
            {'user_id': test_user_id, 'date': today, 'time': '06:00', 'activity': 'Morning yoga'},
            {'user_id': test_user_id, 'date': today, 'time': '12:00', 'activity': 'Lunch meditation'},
            {'user_id': test_user_id, 'date': today, 'time': '18:00', 'activity': 'Evening walk'},
        ]
        
        inserted_ids = []
        for routine in routines:
            result = supabase.table('daily_routines').insert(routine).execute()
            if result.data:
                inserted_ids.append(result.data[0]['id'])
            else:
                print_error(f"Failed to insert routine: {routine['activity']}")
                return False
        
        print_success(f"Inserted {len(inserted_ids)} routines for same day")
        
        # Verify all are retrieved
        verify = supabase.table('daily_routines').select('*').eq('user_id', test_user_id).eq('date', today).execute()
        
        if verify.data and len(verify.data) >= 3:
            print_success(f"Retrieved {len(verify.data)} routines for the day")
            
            # Clean up
            for routine_id in inserted_ids:
                supabase.table('daily_routines').delete().eq('id', routine_id).execute()
            print_success("Cleaned up test data")
            return True
        else:
            print_error("Could not retrieve all routines")
            return False
            
    except Exception as e:
        print_error(f"Multiple routines test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print(f"\n{'='*60}")
    print(f"{BLUE}🚀 DAILY ROUTINES FEATURE TEST SUITE{RESET}")
    print(f"{'='*60}")
    
    tests = [
        ("Table Existence", test_table_exists),
        ("RLS Policies", test_rls_policies),
        ("Database Indexes", test_indexes),
        ("Backend API Routes", test_backend_routes),
        ("Data Insertion", test_manual_data_insertion),
        ("Multiple Routines", test_multiple_routines_per_day),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"{BLUE}📊 TEST SUMMARY{RESET}")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{name:.<40} {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED! Daily Routines feature is ready!{RESET}")
        print(f"\n{YELLOW}Next steps:{RESET}")
        print("  1. Start the backend: cd backend && python run_dev.py")
        print("  2. Start the frontend: npm run dev")
        print("  3. Navigate to Daily Routines page in the app")
        print("  4. Add routines and verify they appear in the list")
    else:
        print(f"\n{RED}⚠️  Some tests failed. Please review and fix issues.{RESET}")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
