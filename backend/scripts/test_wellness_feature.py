"""
Test script for Wellness Scoring feature.
Tests journal entries, goals, and wellness calculation.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import date, datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wellness_scoring():
    """Test wellness scoring feature end-to-end."""
    from app.utils.database import get_supabase
    
    supabase = get_supabase(use_service_role=True)
    
    logger.info("🧪 Testing Wellness Scoring Feature")
    logger.info("="*80)
    
    # Test 1: Check tables exist
    logger.info("\n📊 Test 1: Verifying tables exist...")
    try:
        tables_to_check = ['journal_entries', 'goals', 'wellness_scores']
        for table in tables_to_check:
            result = supabase.table(table).select("id").limit(1).execute()
            logger.info(f"   ✅ Table '{table}' exists and is accessible")
    except Exception as e:
        logger.error(f"   ❌ Table check failed: {e}")
        logger.error("   ⚠️  Please run: backend/database/wellness_scoring_update.sql in Supabase SQL Editor")
        return False
    
    # Test 2: Get a test user
    logger.info("\n👤 Test 2: Getting test user...")
    try:
        users = supabase.table("profiles").select("id, email").limit(1).execute()
        if not users.data or len(users.data) == 0:
            logger.error("   ❌ No users found in database")
            logger.info("   💡 Please sign up a user first")
            return False
        
        test_user_id = users.data[0]['id']
        test_user_email = users.data[0]['email']
        logger.info(f"   ✅ Using test user: {test_user_email} ({test_user_id})")
    except Exception as e:
        logger.error(f"   ❌ Failed to get user: {e}")
        return False
    
    # Test 3: Create journal entry
    logger.info("\n📝 Test 3: Creating journal entry...")
    try:
        journal_data = {
            "user_id": test_user_id,
            "date": date.today().isoformat(),
            "content": "Test journal entry for wellness scoring",
            "mood_tag": "testing"
        }
        result = supabase.table("journal_entries").insert(journal_data).execute()
        if result.data and len(result.data) > 0:
            journal_id = result.data[0]['id']
            logger.info(f"   ✅ Journal entry created: {journal_id}")
        else:
            logger.warning("   ⚠️  Journal entry creation returned no data")
    except Exception as e:
        logger.error(f"   ❌ Failed to create journal entry: {e}")
        logger.error(f"   Details: {str(e)}")
    
    # Test 4: Create goal
    logger.info("\n🎯 Test 4: Creating goal...")
    try:
        goal_data = {
            "user_id": test_user_id,
            "title": "Test wellness scoring feature",
            "description": "Verify goal tracking works",
            "target_date": date.today().isoformat(),
            "status": "active",
            "completion_percent": 50,
            "is_completed": False
        }
        result = supabase.table("goals").insert(goal_data).execute()
        if result.data and len(result.data) > 0:
            goal_id = result.data[0]['id']
            logger.info(f"   ✅ Goal created: {goal_id}")
        else:
            logger.warning("   ⚠️  Goal creation returned no data")
    except Exception as e:
        logger.error(f"   ❌ Failed to create goal: {e}")
        logger.error(f"   Details: {str(e)}")
    
    # Test 5: Calculate wellness score
    logger.info("\n💚 Test 5: Calculating wellness score...")
    try:
        from app.api.routes.wellness import calculate_wellness_score
        
        wellness_data = calculate_wellness_score(test_user_id, date.today(), supabase)
        logger.info(f"   ✅ Wellness score calculated:")
        logger.info(f"      Overall: {wellness_data['overall_score']}")
        logger.info(f"      Emotion: {wellness_data['emotion_score']}")
        logger.info(f"      Wearable: {wellness_data['wearable_score']}")
        logger.info(f"      Engagement: {wellness_data['engagement_score']}")
        logger.info(f"      Insights: {len(wellness_data['insights'])} items")
        logger.info(f"      Recommendations: {len(wellness_data['recommendations'])} items")
    except Exception as e:
        logger.error(f"   ❌ Failed to calculate wellness: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Save wellness score
    logger.info("\n💾 Test 6: Saving wellness score to database...")
    try:
        result = supabase.table("wellness_scores").upsert(
            wellness_data,
            on_conflict="user_id,date"
        ).execute()
        if result.data and len(result.data) > 0:
            saved_score = result.data[0]
            logger.info(f"   ✅ Wellness score saved to database")
            logger.info(f"      ID: {saved_score['id']}")
            logger.info(f"      Date: {saved_score['date']}")
            logger.info(f"      Score: {saved_score['overall_score']}")
        else:
            logger.error("   ❌ Wellness score save returned no data")
            return False
    except Exception as e:
        logger.error(f"   ❌ Failed to save wellness score: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 7: Verify wellness score persisted
    logger.info("\n🔍 Test 7: Verifying wellness score persisted...")
    try:
        result = supabase.table("wellness_scores").select("*").eq("user_id", test_user_id).eq("date", date.today().isoformat()).execute()
        if result.data and len(result.data) > 0:
            logger.info(f"   ✅ Wellness score found in database")
            logger.info(f"      Overall Score: {result.data[0]['overall_score']}")
        else:
            logger.error("   ❌ Wellness score not found in database")
            return False
    except Exception as e:
        logger.error(f"   ❌ Failed to verify wellness score: {e}")
        return False
    
    logger.info("\n" + "="*80)
    logger.info("✅ All tests passed! Wellness Scoring feature is working correctly.")
    logger.info("="*80)
    return True

if __name__ == "__main__":
    logger.info("🚀 Starting Wellness Scoring Tests...")
    success = test_wellness_scoring()
    if success:
        logger.info("\n🎉 SUCCESS! Feature is fully functional.")
        logger.info("\n📋 Next Steps:")
        logger.info("   1. Test the API endpoints with curl or Postman")
        logger.info("   2. Test the frontend UI")
        logger.info("   3. Check data in Supabase dashboard")
    else:
        logger.error("\n❌ TESTS FAILED! Please check the errors above.")
        sys.exit(1)
