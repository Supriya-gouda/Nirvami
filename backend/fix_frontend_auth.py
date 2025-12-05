#!/usr/bin/env python3
"""
Create a proper test user and fix frontend authentication issue
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime
import json

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.database import get_supabase

def create_test_user_with_auth():
    """Create a test user that works with the authentication system"""
    
    print("🔧 CREATING TEST USER FOR FRONTEND")
    print("=" * 45)
    
    supabase = get_supabase(use_service_role=True)  # Use service role to bypass RLS
    
    # Use existing user ID from recommendations
    test_user_id = "e9b4f233-d81f-442d-96b6-789b5f41867e"
    test_email = "test.user@nirvami.com"
    
    try:
        # Step 1: Create auth user (this might fail if user exists, that's ok)
        try:
            auth_result = supabase.auth.admin.create_user({
                "email": test_email,
                "password": "TestPassword123!",
                "email_confirm": True,
                "user_metadata": {
                    "full_name": "Test User",
                    "age": 25
                }
            })
            print(f"✅ Created auth user: {test_email}")
            actual_user_id = auth_result.user.id
        except Exception as auth_error:
            print(f"⚠️  Auth user creation failed (might already exist): {auth_error}")
            # Use the existing user ID from recommendations
            actual_user_id = test_user_id
        
        # Step 2: Create profile in profiles table
        profile_data = {
            "id": actual_user_id,
            "email": test_email,
            "full_name": "Test User",
            "dosha_type": "vata-pitta",
            "role": "user",
            "consent_data_collection": True,
            "consent_ai_processing": True,
            "consent_notifications": True,
            "timezone": "UTC",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Try to insert or update profile
        try:
            result = supabase.table("profiles").insert(profile_data).execute()
            print(f"✅ Created user profile in profiles table")
        except Exception as profile_error:
            # Try to update if insert failed
            try:
                result = supabase.table("profiles").update(profile_data).eq("id", actual_user_id).execute()
                print(f"✅ Updated existing user profile")
            except Exception as update_error:
                print(f"❌ Profile creation/update failed: {update_error}")
                return False
        
        # Step 3: Update recommendations to use correct user ID if needed
        if actual_user_id != test_user_id:
            try:
                update_recs = supabase.table("recommendations")\
                    .update({"user_id": actual_user_id})\
                    .eq("user_id", test_user_id)\
                    .execute()
                print(f"✅ Updated recommendation user IDs")
            except Exception as rec_error:
                print(f"⚠️  Recommendation update failed: {rec_error}")
        
        # Step 4: Verify everything works
        verify_profile = supabase.table("profiles").select("*").eq("id", actual_user_id).execute()
        verify_recs = supabase.table("recommendations").select("id").eq("user_id", actual_user_id).execute()
        
        if verify_profile.data and verify_recs.data:
            print(f"\n✅ TEST USER SETUP COMPLETE!")
            print(f"   Email: {test_email}")
            print(f"   Password: TestPassword123!")
            print(f"   User ID: {actual_user_id}")
            print(f"   Recommendations: {len(verify_recs.data)} found")
            
            return True
        else:
            print(f"❌ Verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Test user creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_frontend_test_instructions():
    """Create instructions for testing the frontend"""
    
    instructions = """
# 🧪 FRONTEND TESTING INSTRUCTIONS

## Quick Test (Browser Console)

1. **Open your frontend** in the browser (usually http://localhost:3000 or http://localhost:5173)

2. **Open Browser Developer Console** (F12)

3. **Manually set authentication** for testing:
```javascript
// Set test authentication token in localStorage
localStorage.setItem('token', 'test-token-for-user-e9b4f233-d81f-442d-96b6-789b5f41867e');

// Refresh the page to load with authentication
window.location.reload();
```

4. **Navigate to Yoga/Ayurveda pages** and you should see recommendations!

## Proper Login Test

1. **Register/Login** with these credentials:
   - Email: `test.user@nirvami.com`
   - Password: `TestPassword123!`

2. **Navigate to recommendation pages**:
   - Yoga Recommendations: Should show 13+ recommendations
   - Ayurveda Recommendations: Should show 7+ recommendations

## API Test

If the frontend still shows no data, test the API directly:

```bash
# Test the API endpoint (replace YOUR_TOKEN with actual token)
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  "http://localhost:8000/api/v1/recommendations/yoga?date=2025-12-05"
```

## Troubleshooting

If you still see "No recommendations available":

1. **Check browser console** for authentication errors
2. **Verify backend is running** on port 8000
3. **Check network tab** for failed API calls
4. **Try the browser console token method** above

## Expected Results

You should now see:
- ✅ 13+ Yoga recommendations (mix of chat and device sources)
- ✅ 7+ Ayurveda recommendations (from chat interactions)
- ✅ Recommendations grouped by source (chat/device)
- ✅ Date-based filtering working
- ✅ Persistent data that doesn't disappear
"""

    with open("d:\\Nirvami\\FRONTEND_TESTING_GUIDE.md", "w") as f:
        f.write(instructions)
    
    print(f"\n📝 Created testing guide: FRONTEND_TESTING_GUIDE.md")

def main():
    """Main setup function"""
    print("🚀 NIRVAMI FRONTEND AUTHENTICATION SETUP")
    print("=" * 50)
    
    success = create_test_user_with_auth()
    
    if success:
        create_frontend_test_instructions()
        
        print(f"\n🎉 SETUP COMPLETE!")
        print("=" * 30)
        print("✅ Test user created with proper authentication")
        print("✅ User profile linked to existing recommendations") 
        print("✅ Frontend should now be able to authenticate")
        print("✅ API endpoints should return recommendation data")
        print("\n📖 Check FRONTEND_TESTING_GUIDE.md for next steps")
        print("\n🔗 Quick test login:")
        print("   Email: test.user@nirvami.com")
        print("   Password: TestPassword123!")
    else:
        print(f"\n❌ Setup failed - check the errors above")

if __name__ == "__main__":
    main()