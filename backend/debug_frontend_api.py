#!/usr/bin/env python3
"""
Debug API endpoint calls to understand why frontend shows no recommendations
"""

import asyncio
import sys
import os
import uuid
from datetime import date, datetime
import requests
import json

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.database import get_supabase
from app.services.recommendation_service import recommendation_service

async def test_api_endpoints():
    """Test the API endpoints that frontend is calling"""
    
    print("🔍 TESTING API ENDPOINTS DIRECTLY")
    print("=" * 50)
    
    # Get a real user from the database
    supabase = get_supabase()
    result = supabase.table("recommendations").select("user_id").limit(1).execute()
    
    if not result.data:
        print("❌ No recommendations found in database")
        return False
        
    real_user_id = result.data[0]["user_id"]
    print(f"✅ Testing with user ID: {real_user_id[:8]}...")
    
    # Test backend service directly
    print(f"\n📊 BACKEND SERVICE TEST")
    print("-" * 30)
    
    try:
        # Test get_recommendations_by_category directly
        yoga_recs = await recommendation_service.get_recommendations_by_category(
            user_id=real_user_id,
            category="yoga", 
            target_date=date.today()
        )
        
        ayurveda_recs = await recommendation_service.get_recommendations_by_category(
            user_id=real_user_id,
            category="ayurveda",
            target_date=date.today()
        )
        
        daily_recs = await recommendation_service.get_daily_recommendations(
            user_id=real_user_id,
            target_date=date.today()
        )
        
        print(f"✅ Direct service call - Yoga: {len(yoga_recs)} recommendations")
        print(f"✅ Direct service call - Ayurveda: {len(ayurveda_recs)} recommendations")
        print(f"✅ Direct service call - Daily total: {len(daily_recs.yoga)} yoga, {len(daily_recs.ayurveda)} ayurveda")
        
        # Show sample data
        if yoga_recs:
            print(f"\n📝 Sample yoga recommendations:")
            for i, rec in enumerate(yoga_recs[:3], 1):
                print(f"   {i}. {rec.title} (from {rec.source.value})")
        
        if ayurveda_recs:
            print(f"\n🌿 Sample ayurveda recommendations:")
            for i, rec in enumerate(ayurveda_recs[:3], 1):
                print(f"   {i}. {rec.title} (from {rec.source.value})")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_user_authentication():
    """Check if there are actual users in the profiles table"""
    
    print(f"\n👤 CHECKING USER PROFILES")
    print("-" * 30)
    
    try:
        supabase = get_supabase()
        
        # Check profiles table
        profiles_result = supabase.table("profiles").select("id, email").limit(5).execute()
        
        if profiles_result.data:
            print(f"✅ Found {len(profiles_result.data)} user profiles:")
            for profile in profiles_result.data:
                print(f"   - {profile['email']} (ID: {profile['id'][:8]}...)")
        else:
            print("❌ No user profiles found in database")
            return False
        
        # Check if recommendation user_ids match profile IDs
        recs_result = supabase.table("recommendations").select("user_id").limit(5).execute()
        
        if recs_result.data:
            rec_user_ids = [rec["user_id"] for rec in recs_result.data]
            profile_ids = [profile["id"] for profile in profiles_result.data]
            
            print(f"\n🔗 Checking ID matching:")
            for rec_user_id in set(rec_user_ids):
                if rec_user_id in profile_ids:
                    print(f"   ✅ Recommendation user ID {rec_user_id[:8]}... matches profile")
                else:
                    print(f"   ⚠️  Recommendation user ID {rec_user_id[:8]}... NOT in profiles table")
        
        return True
        
    except Exception as e:
        print(f"❌ User authentication check failed: {e}")
        return False

async def test_frontend_data_structure():
    """Test the data structure that frontend expects"""
    
    print(f"\n🌐 TESTING FRONTEND DATA STRUCTURE")
    print("-" * 40)
    
    try:
        # Get a real user from profiles table
        supabase = get_supabase()
        profiles_result = supabase.table("profiles").select("id").limit(1).execute()
        
        if not profiles_result.data:
            print("❌ No user profiles found")
            return False
            
        user_id = profiles_result.data[0]["id"]
        
        # Test daily recommendations response format
        daily_recs = await recommendation_service.get_daily_recommendations(
            user_id=user_id,
            target_date=date.today()
        )
        
        print(f"📅 Daily recommendations format:")
        print(f"   Date: {daily_recs.date}")
        print(f"   Yoga: {len(daily_recs.yoga)} items")
        print(f"   Ayurveda: {len(daily_recs.ayurveda)} items")
        print(f"   Lifestyle: {len(daily_recs.lifestyle)} items")
        print(f"   Sleep: {len(daily_recs.sleep)} items")
        print(f"   Breathing: {len(daily_recs.breathing)} items")
        print(f"   Meditation: {len(daily_recs.meditation)} items")
        print(f"   Diet: {len(daily_recs.diet)} items")
        
        # Test if data structure matches frontend expectations
        if daily_recs.yoga and len(daily_recs.yoga) > 0:
            sample_rec = daily_recs.yoga[0]
            print(f"\n📝 Sample recommendation structure:")
            print(f"   ID: {sample_rec.id}")
            print(f"   Title: {sample_rec.title}")
            print(f"   Content: {sample_rec.content[:50]}...")
            print(f"   Source: {sample_rec.source.value}")
            print(f"   Category: {sample_rec.category.value}")
            print(f"   Date: {sample_rec.date}")
        
        return len(daily_recs.yoga) > 0 or len(daily_recs.ayurveda) > 0
        
    except Exception as e:
        print(f"❌ Frontend data structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run comprehensive API debugging"""
    print("🔬 NIRVAMI API DEBUGGING - FRONTEND INTEGRATION")
    print("=" * 60)
    
    tests = [
        ("API Endpoints", test_api_endpoints),
        ("User Authentication", test_user_authentication),
        ("Frontend Data Structure", test_frontend_data_structure),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n🎯 DEBUGGING SUMMARY")
    print("=" * 25)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n✅ Backend APIs are working correctly!")
        print("   The issue might be in frontend authentication or API calls")
    else:
        print(f"\n⚠️  Some backend tests failed")
        print("   Check the output above for specific issues")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())