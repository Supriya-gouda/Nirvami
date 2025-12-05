#!/usr/bin/env python3
"""
Enhanced Debug script for recommendation system - tests both chat and wearable recommendations
"""

import asyncio
import sys
import os
import uuid
from datetime import date, timedelta, datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.recommendation_service import recommendation_service
from app.services.wearable_service_v2 import WearableService
from app.utils.database import get_supabase

# Use a proper UUID for testing
TEST_USER_ID = str(uuid.uuid4())

async def test_table_exists():
    """Check if recommendations table exists"""
    print("\n🔍 TESTING TABLE EXISTENCE")
    print("=" * 50)
    
    try:
        supabase = get_supabase()
        
        # Try to query the table
        result = supabase.table("recommendations").select("count", count="exact").execute()
        
        print(f"✅ Recommendations table exists!")
        print(f"   Total records: {result.count}")
        return True
    except Exception as e:
        print(f"❌ Recommendations table might not exist: {e}")
        print("\n📝 SQL to create the table:")
        print("""
-- Run this in Supabase SQL Editor:
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('chat', 'device', 'manual')),
    category TEXT NOT NULL CHECK (category IN ('yoga', 'ayurveda', 'lifestyle', 'sleep', 'breathing', 'meditation', 'diet')),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date, title, category)
);

CREATE INDEX idx_recommendations_user_date ON recommendations(user_id, date);
CREATE INDEX idx_recommendations_category ON recommendations(category);
        """)
        return False

async def test_chat_recommendations():
    """Test chat recommendation extraction"""
    print("\n💬 TESTING CHAT RECOMMENDATIONS")
    print("=" * 50)
    
    # Sample chat response with yoga and ayurveda recommendations
    sample_chat = """
Based on your health data, here are my personalized recommendations:

**Yoga Recommendations:**
• Practice gentle Hatha yoga poses to improve flexibility
• Try 10-minute morning sun salutations for energy
• Evening restorative yoga poses before bed for better sleep

**Ayurveda Recommendations:**  
• Drink warm ginger tea in the morning to boost digestion
• Eat light, easily digestible foods for dinner
• Practice oil pulling with sesame oil for oral health
• Try abhyanga (self-massage) with warm oils before bathing

**Lifestyle Recommendations:**
• Maintain regular sleep schedule (bed by 10pm)
• Take short walks after meals to aid digestion
• Practice 5-minute breathing exercises twice daily

I hope these recommendations help improve your overall wellness!
    """
    
    try:
        recommendations = await recommendation_service.extract_and_store_recommendations_from_chat(
            user_id=TEST_USER_ID,
            message_text=sample_chat,  # Correct parameter name
            timestamp=datetime.now()   # Add required timestamp
        )
        
        print(f"✅ Extracted and stored {len(recommendations)} chat recommendations")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. [{rec.category.value.upper()}] {rec.title}")
        
        return len(recommendations) > 0
        
    except Exception as e:
        print(f"❌ Chat recommendation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_wearable_recommendations():
    """Test wearable/device recommendation extraction"""
    print("\n⌚ TESTING WEARABLE RECOMMENDATIONS")
    print("=" * 50)
    
    # Sample device recommendations (like what would come from health analysis)
    sample_device_recs = [
        "Try relaxation yoga before bed for better sleep quality",
        "Practice deep breathing exercises during high stress periods",
        "Consider light yoga stretches after long periods of sitting",
        "Drink herbal tea (chamomile or ashwagandha) in the evening",
        "Take short movement breaks every hour during work",
        "Practice meditation for 5-10 minutes when stress levels are high"
    ]
    
    try:
        stored_recs = await recommendation_service.save_device_recommendations(
            user_id=TEST_USER_ID,
            target_date=date.today(),
            device_recs=sample_device_recs
        )
        
        print(f"✅ Stored {len(stored_recs)} device recommendations")
        for i, rec in enumerate(stored_recs, 1):
            print(f"   {i}. [{rec.category.value.upper()}] {rec.title}")
        
        return len(stored_recs) > 0
        
    except Exception as e:
        print(f"❌ Device recommendation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_retrieval():
    """Test retrieving recommendations"""
    print("\n📖 TESTING RECOMMENDATION RETRIEVAL")
    print("=" * 50)
    
    try:
        # Test daily recommendations
        daily_recs = await recommendation_service.get_daily_recommendations(
            user_id=TEST_USER_ID,
            target_date=date.today()
        )
        
        print(f"📅 Daily recommendations for {daily_recs.date}:")
        print(f"   🧘 Yoga: {len(daily_recs.yoga)} recommendations")
        print(f"   🌿 Ayurveda: {len(daily_recs.ayurveda)} recommendations") 
        print(f"   🏃 Lifestyle: {len(daily_recs.lifestyle)} recommendations")
        print(f"   😴 Sleep: {len(daily_recs.sleep)} recommendations")
        print(f"   🫁 Breathing: {len(daily_recs.breathing)} recommendations")
        print(f"   🧘‍♀️ Meditation: {len(daily_recs.meditation)} recommendations")
        print(f"   🥗 Diet: {len(daily_recs.diet)} recommendations")
        
        # Test category-specific retrieval
        yoga_recs = await recommendation_service.get_recommendations_by_category(
            user_id=TEST_USER_ID,
            category="yoga",
            target_date=date.today()
        )
        
        print(f"\n🧘 Yoga recommendations details:")
        for i, rec in enumerate(yoga_recs, 1):
            print(f"   {i}. {rec.title} (from {rec.source.value})")
        
        total_found = sum([
            len(daily_recs.yoga),
            len(daily_recs.ayurveda), 
            len(daily_recs.lifestyle),
            len(daily_recs.sleep),
            len(daily_recs.breathing),
            len(daily_recs.meditation),
            len(daily_recs.diet)
        ])
        
        return total_found > 0
        
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_persistence():
    """Test recommendation persistence across dates"""
    print("\n💾 TESTING RECOMMENDATION PERSISTENCE")
    print("=" * 50)
    
    try:
        # Check today
        today_recs = await recommendation_service.get_daily_recommendations(
            user_id=TEST_USER_ID,
            target_date=date.today()
        )
        
        # Check yesterday (should be empty unless we stored something)
        yesterday_recs = await recommendation_service.get_daily_recommendations(
            user_id=TEST_USER_ID,
            target_date=date.today() - timedelta(days=1)
        )
        
        print(f"📅 Today ({date.today()}): Found recommendations")
        print(f"📅 Yesterday ({date.today() - timedelta(days=1)}): Found recommendations")
        
        total_today = sum([
            len(today_recs.yoga), len(today_recs.ayurveda), len(today_recs.lifestyle),
            len(today_recs.sleep), len(today_recs.breathing), len(today_recs.meditation),
            len(today_recs.diet)
        ])
        
        total_yesterday = sum([
            len(yesterday_recs.yoga), len(yesterday_recs.ayurveda), len(yesterday_recs.lifestyle),
            len(yesterday_recs.sleep), len(yesterday_recs.breathing), len(yesterday_recs.meditation),
            len(yesterday_recs.diet)
        ])
        
        print(f"   Today: {total_today} total recommendations")
        print(f"   Yesterday: {total_yesterday} total recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        return False

async def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 CLEANING UP TEST DATA")
    print("=" * 30)
    
    try:
        supabase = get_supabase()
        
        # Delete test user's recommendations
        result = supabase.table("recommendations")\
            .delete()\
            .eq("user_id", TEST_USER_ID)\
            .execute()
        
        print(f"✅ Cleaned up test data")
        
    except Exception as e:
        print(f"⚠️  Cleanup failed (this is okay): {e}")

async def main():
    """Main test runner"""
    print("🔬 NIRVAMI RECOMMENDATION SYSTEM DEBUG v2")
    print("=" * 60)
    
    # Test table existence first
    table_exists = await test_table_exists()
    
    if not table_exists:
        print("\n❌ Cannot continue tests - recommendations table does not exist")
        print("   Please run the SQL commands shown above in Supabase first")
        return
    
    # Run all tests
    tests = [
        ("Chat Recommendations", test_chat_recommendations),
        ("Wearable Recommendations", test_wearable_recommendations),
        ("Retrieval", test_retrieval),
        ("Persistence", test_persistence),
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
    print("=" * 30)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n🎉 All tests passed! Recommendation system is working.")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
    
    # Cleanup
    await cleanup_test_data()
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())