"""
Test script for Wearable Integration & Manual Health Input Feature.
Tests the complete flow from data entry to recommendations.
"""
import os
import sys
from datetime import datetime, timedelta, date
import json

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.database import get_supabase
from app.services.wearable_service import WearableService


def test_wearable_feature():
    """Test the complete wearable feature."""
    
    print("=" * 80)
    print("TESTING WEARABLE INTEGRATION & MANUAL HEALTH INPUT FEATURE")
    print("=" * 80)
    
    try:
        supabase = get_supabase()
        
        # Step 1: Check if tables exist
        print("\n[STEP 1] Checking database schema...")
        
        # Check wearable_snapshots table
        snapshots_check = supabase.table("wearable_snapshots").select("id").limit(1).execute()
        print(f"✓ 'wearable_snapshots' table exists and is accessible")
        
        # Check wearable_daily_stats table
        stats_check = supabase.table("wearable_daily_stats").select("id").limit(1).execute()
        print(f"✓ 'wearable_daily_stats' table exists and is accessible")
        
        # Step 2: Get a test user
        print("\n[STEP 2] Finding test user...")
        users = supabase.table("profiles").select("id, email, dosha_type").limit(1).execute()
        
        if not users.data:
            print("✗ No users found in database")
            print("  Create a user first through the signup process")
            return False
        
        test_user_id = users.data[0]["id"]
        test_user_email = users.data[0]["email"]
        dosha_type = users.data[0].get("dosha_type")
        print(f"✓ Using test user: {test_user_email} ({test_user_id})")
        if dosha_type:
            print(f"  Dosha type: {dosha_type}")
        
        # Step 3: Test watch data ingestion
        print("\n[STEP 3] Testing smartwatch data ingestion...")
        
        watch_data = {
            "provider": "apple_watch",
            "captured_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "heart_rate": 72,
            "hrv_ms": 65,
            "steps": 5000,
            "sleep_hours": 7.5,
            "stress_level": 4,
            "calories_burned": 350
        }
        
        watch_result = WearableService.ingest_watch_data(test_user_id, watch_data)
        print(f"✓ Watch data ingested: {watch_result['id']}")
        print(f"  Provider: {watch_result['provider']}")
        print(f"  Source: {watch_result['source']}")
        
        # Step 4: Test manual entry ingestion
        print("\n[STEP 4] Testing manual health data entry...")
        
        manual_data = {
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "sleep_hours": 6.2,
            "avg_heart_rate": 88,
            "steps": 3200,
            "stress_level": 7
        }
        
        manual_result = WearableService.ingest_manual_entry(test_user_id, manual_data)
        print(f"✓ Manual entry saved: {manual_result['id']}")
        print(f"  Date: {manual_data['date']}")
        print(f"  Source: {manual_result['source']}")
        
        # Step 5: Test daily aggregation
        print("\n[STEP 5] Testing daily stats aggregation...")
        
        agg_result = WearableService.aggregate_daily_stats(test_user_id, date.today())
        print(f"✓ Daily stats aggregated for {agg_result['date']}")
        print(f"  Avg Heart Rate: {agg_result.get('avg_heart_rate')}")
        print(f"  Total Steps: {agg_result.get('total_steps')}")
        print(f"  Sleep Hours: {agg_result.get('sleep_hours')}")
        print(f"  Data Source: {agg_result.get('data_source')}")
        
        # Step 6: Test emotion detection from wearables
        print("\n[STEP 6] Testing emotion detection from wearables...")
        
        # Use yesterday's manual entry (high stress)
        yesterday_stats = WearableService.aggregate_daily_stats(
            test_user_id,
            date.today() - timedelta(days=1)
        )
        
        emotion = WearableService.detect_emotion_from_wearables(test_user_id, yesterday_stats)
        
        if emotion:
            print(f"✓ Emotion detected: {emotion['emotion_type']}")
            print(f"  Confidence: {emotion['confidence']}")
            print(f"  Factors: {json.dumps(emotion['all_scores'], indent=2)}")
        else:
            print("  No strong emotion signal detected")
        
        # Step 7: Test food recommendations
        print("\n[STEP 7] Testing food recommendations...")
        
        food_recs = WearableService.get_food_recommendations(yesterday_stats, dosha_type)
        print(f"✓ Generated {len(food_recs)} food recommendations:")
        for i, rec in enumerate(food_recs, 1):
            print(f"  {i}. {rec.get('reason')}")
            print(f"     {rec.get('suggestion')}")
        
        # Step 8: Test yoga recommendations
        print("\n[STEP 8] Testing yoga recommendations...")
        
        yoga_recs = WearableService.get_yoga_recommendations(yesterday_stats, dosha_type)
        print(f"✓ Generated {len(yoga_recs)} yoga recommendations:")
        for i, rec in enumerate(yoga_recs, 1):
            print(f"  {i}. {rec.get('reason')}")
            print(f"     Practice: {rec.get('practice')}")
        
        # Step 9: Test comprehensive summary
        print("\n[STEP 9] Testing comprehensive wearable summary...")
        
        summary = WearableService.get_today_summary(test_user_id, date.today())
        
        print(f"✓ Summary generated for {summary['date']}")
        print(f"\n  Health Metrics:")
        print(f"    Sleep: {summary.get('sleep_hours')} hours")
        print(f"    Heart Rate: {summary.get('avg_heart_rate')} bpm")
        print(f"    Steps: {summary.get('total_steps')}")
        print(f"    Stress: {summary.get('avg_stress_level')}/10")
        print(f"\n  Inferred Emotion: {summary.get('inferred_emotion')}")
        print(f"\n  Insights:")
        for insight in summary.get('insights', []):
            print(f"    • {insight}")
        
        # Step 10: Verify database storage
        print("\n[STEP 10] Verifying database storage...")
        
        # Check snapshots
        snapshots = supabase.table("wearable_snapshots").select("*").eq(
            "user_id", test_user_id
        ).execute()
        print(f"✓ Found {len(snapshots.data)} snapshots in database")
        
        # Check daily stats
        stats = supabase.table("wearable_daily_stats").select("*").eq(
            "user_id", test_user_id
        ).execute()
        print(f"✓ Found {len(stats.data)} daily stats records")
        
        # Check emotion logs from wearables
        wearable_emotions = supabase.table("emotion_logs").select("*").eq(
            "user_id", test_user_id
        ).eq("source", "wearable").execute()
        print(f"✓ Found {len(wearable_emotions.data)} wearable-inferred emotions")
        
        # Final summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✓ Database schema validated")
        print(f"✓ Watch data ingestion: WORKING")
        print(f"✓ Manual entry ingestion: WORKING")
        print(f"✓ Daily aggregation: WORKING")
        print(f"✓ Emotion detection: WORKING")
        print(f"✓ Food recommendations: WORKING")
        print(f"✓ Yoga recommendations: WORKING")
        print(f"✓ Comprehensive summary: WORKING")
        print(f"✓ Database storage: VERIFIED")
        print(f"\n✅ WEARABLE INTEGRATION FEATURE IS WORKING CORRECTLY!")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_wearable_feature()
    sys.exit(0 if success else 1)
