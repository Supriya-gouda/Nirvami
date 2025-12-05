#!/usr/bin/env python3
"""
Simple test to verify recommendation system is working with real user IDs
"""

import asyncio
import sys
import os
import uuid
from datetime import date, timedelta, datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.recommendation_service import recommendation_service
from app.utils.database import get_supabase

async def test_with_real_user():
    """Test with a real user from the database"""
    
    print("🔍 FINDING REAL USER")
    print("=" * 30)
    
    # Get a real user ID from the database
    try:
        supabase = get_supabase()
        
        # Get existing recommendations to find a real user ID
        existing_recs = supabase.table("recommendations").select("user_id").limit(1).execute()
        
        if existing_recs.data:
            real_user_id = existing_recs.data[0]["user_id"]
            print(f"✅ Found real user ID: {real_user_id[:8]}...")
        else:
            print("❌ No existing recommendations found")
            return False
        
    except Exception as e:
        print(f"❌ Error finding real user: {e}")
        return False
    
    # Test with unique content that won't duplicate
    unique_timestamp = datetime.now().isoformat()
    
    print(f"\n💬 TESTING CHAT EXTRACTION")
    print("=" * 40)
    
    unique_chat = f"""
Based on your current wellness analysis, here are personalized recommendations for {unique_timestamp}:

**Yoga Recommendations:**
• Practice unique evening flow sequence #{unique_timestamp[-6:]}
• Try specialized breathing technique for stress relief
• Perform custom meditation posture for focus

**Ayurveda Recommendations:**  
• Drink specialized herbal blend for your dosha type
• Practice unique self-massage technique with lavender oil
• Try personalized digestive tea after dinner

**Lifestyle Recommendations:**
• Implement custom sleep hygiene routine
• Take mindful nature walks during sunset hours
• Practice gratitude journaling before bed

These recommendations are uniquely tailored for your wellness journey!
    """
    
    try:
        recommendations = await recommendation_service.extract_and_store_recommendations_from_chat(
            user_id=real_user_id,
            message_text=unique_chat,
            timestamp=datetime.now()
        )
        
        print(f"✅ Successfully extracted and stored {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. [{rec.category.value.upper()}] {rec.title}")
        
        return len(recommendations) > 0
        
    except Exception as e:
        print(f"❌ Chat extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_retrieval_with_real_user():
    """Test retrieving recommendations for real user"""
    
    print(f"\n📖 TESTING RETRIEVAL")
    print("=" * 30)
    
    try:
        supabase = get_supabase()
        existing_recs = supabase.table("recommendations").select("user_id").limit(1).execute()
        real_user_id = existing_recs.data[0]["user_id"]
        
        # Get today's recommendations
        daily_recs = await recommendation_service.get_daily_recommendations(
            user_id=real_user_id,
            target_date=date.today()
        )
        
        print(f"📅 Daily recommendations for {daily_recs.date}:")
        categories = [
            ('yoga', daily_recs.yoga),
            ('ayurveda', daily_recs.ayurveda),
            ('lifestyle', daily_recs.lifestyle),
            ('sleep', daily_recs.sleep),
            ('breathing', daily_recs.breathing),
            ('meditation', daily_recs.meditation),
            ('diet', daily_recs.diet)
        ]
        
        total = 0
        for cat_name, cat_recs in categories:
            count = len(cat_recs)
            total += count
            emoji = {'yoga': '🧘', 'ayurveda': '🌿', 'lifestyle': '🏃', 'sleep': '😴', 'breathing': '🫁', 'meditation': '🧘‍♀️', 'diet': '🥗'}
            print(f"   {emoji.get(cat_name, '📝')} {cat_name.title()}: {count} recommendations")
            
            # Show first few titles
            if count > 0:
                for rec in cat_recs[:2]:  # Show first 2
                    print(f"      → {rec.title} (from {rec.source.value})")
        
        print(f"\n💫 Total: {total} recommendations found")
        return total > 0
        
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("🔬 NIRVAMI RECOMMENDATION SYSTEM - REAL USER TEST")
    print("=" * 55)
    
    tests = [
        ("Chat Extraction", test_with_real_user),
        ("Recommendation Retrieval", test_retrieval_with_real_user),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 20)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n🎉 All tests passed! Recommendation system is working correctly.")
        print(f"✅ Chat recommendations are being extracted and stored")
        print(f"✅ Recommendations can be retrieved by date and category")
        print(f"✅ The system is ready for use!")
    else:
        print(f"\n⚠️  Some tests failed. Check the logs for details.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())