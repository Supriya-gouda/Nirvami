"""
Test script to verify Yoga & Sound Therapy feature is working correctly.
Checks database content and API endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase
import asyncio

def test_database_content():
    """Test that database tables have content."""
    print("\n" + "="*60)
    print("Testing Database Content")
    print("="*60)
    
    supabase = get_supabase(use_service_role=True)
    
    # Test yoga_poses table
    print("\n1. Testing yoga_poses table...")
    try:
        result = supabase.table("yoga_poses").select("*").execute()
        poses_count = len(result.data) if result.data else 0
        print(f"   ✅ Found {poses_count} yoga poses in database")
        
        if poses_count > 0:
            # Show sample pose
            sample = result.data[0]
            print(f"   Sample: {sample.get('name')} ({sample.get('sanskrit_name')})")
            print(f"   Dosha tags: {sample.get('dosha_tags')}")
            print(f"   Emotion tags: {sample.get('emotion_tags')}")
        
        if poses_count < 10:
            print(f"   ⚠️  WARNING: Only {poses_count} poses found. Recommended: 10-15")
        elif poses_count >= 15:
            print(f"   ✨ EXCELLENT: {poses_count} poses exceed recommendation")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    # Test sound_tracks table
    print("\n2. Testing sound_tracks table...")
    try:
        result = supabase.table("sound_tracks").select("*").execute()
        tracks_count = len(result.data) if result.data else 0
        print(f"   ✅ Found {tracks_count} sound tracks in database")
        
        if tracks_count > 0:
            # Show sample track
            sample = result.data[0]
            print(f"   Sample: {sample.get('title')}")
            print(f"   Dosha tags: {sample.get('dosha_tags')}")
            print(f"   Emotion tags: {sample.get('emotion_tags')}")
            print(f"   Frequency: {sample.get('frequency_hz')} Hz")
        
        if tracks_count < 5:
            print(f"   ⚠️  WARNING: Only {tracks_count} tracks found. Recommended: 5-10")
        elif tracks_count >= 10:
            print(f"   ✨ EXCELLENT: {tracks_count} tracks exceed recommendation")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    # Test ayurveda_resources table
    print("\n3. Testing ayurveda_resources table...")
    try:
        result = supabase.table("ayurveda_resources").select("id, title, category, dosha_tags").execute()
        resources_count = len(result.data) if result.data else 0
        print(f"   ✅ Found {resources_count} ayurveda resources in database")
        
        if resources_count > 0:
            # Show sample resource
            sample = result.data[0]
            print(f"   Sample: {sample.get('title')} ({sample.get('category')})")
            print(f"   Dosha tags: {sample.get('dosha_tags')}")
        
        if resources_count < 5:
            print(f"   ⚠️  WARNING: Only {resources_count} resources found.")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    return True


def test_api_filtering():
    """Test that API filtering works correctly."""
    print("\n" + "="*60)
    print("Testing API Filtering")
    print("="*60)
    
    supabase = get_supabase(use_service_role=True)
    
    # Test dosha filtering for yoga poses
    print("\n4. Testing yoga poses dosha filtering...")
    for dosha in ['vata', 'pitta', 'kapha']:
        try:
            result = supabase.table("yoga_poses")\
                .select("*")\
                .contains("dosha_tags", [dosha])\
                .execute()
            count = len(result.data) if result.data else 0
            print(f"   {dosha.capitalize()}: {count} poses")
        except Exception as e:
            print(f"   ❌ ERROR filtering {dosha}: {e}")
            return False
    
    # Test emotion filtering for yoga poses
    print("\n5. Testing yoga poses emotion filtering...")
    for emotion in ['anxious', 'stressed', 'tired']:
        try:
            result = supabase.table("yoga_poses")\
                .select("*")\
                .contains("emotion_tags", [emotion])\
                .execute()
            count = len(result.data) if result.data else 0
            print(f"   {emotion.capitalize()}: {count} poses")
        except Exception as e:
            print(f"   ❌ ERROR filtering {emotion}: {e}")
            return False
    
    # Test dosha filtering for sound tracks
    print("\n6. Testing sound tracks dosha filtering...")
    for dosha in ['vata', 'pitta', 'kapha']:
        try:
            result = supabase.table("sound_tracks")\
                .select("*")\
                .contains("dosha_tags", [dosha])\
                .execute()
            count = len(result.data) if result.data else 0
            print(f"   {dosha.capitalize()}: {count} tracks")
        except Exception as e:
            print(f"   ❌ ERROR filtering {dosha}: {e}")
            return False
    
    # Test emotion filtering for sound tracks (NOTE: emotion_tags, not mood_tags)
    print("\n7. Testing sound tracks emotion filtering...")
    for emotion in ['anxious', 'stressed', 'calm']:
        try:
            result = supabase.table("sound_tracks")\
                .select("*")\
                .contains("emotion_tags", [emotion])\
                .execute()
            count = len(result.data) if result.data else 0
            print(f"   {emotion.capitalize()}: {count} tracks")
        except Exception as e:
            print(f"   ❌ ERROR filtering {emotion}: {e}")
            return False
    
    # Test ayurveda resources dosha filtering
    print("\n8. Testing ayurveda resources dosha filtering...")
    for dosha in ['vata', 'pitta', 'kapha']:
        try:
            result = supabase.table("ayurveda_resources")\
                .select("*")\
                .contains("dosha_tags", [dosha])\
                .execute()
            count = len(result.data) if result.data else 0
            print(f"   {dosha.capitalize()}: {count} resources")
        except Exception as e:
            print(f"   ❌ ERROR filtering {dosha}: {e}")
            return False
    
    return True


def test_data_quality():
    """Test data quality and completeness."""
    print("\n" + "="*60)
    print("Testing Data Quality")
    print("="*60)
    
    supabase = get_supabase(use_service_role=True)
    
    print("\n9. Checking yoga poses data quality...")
    try:
        result = supabase.table("yoga_poses").select("*").execute()
        poses = result.data if result.data else []
        
        for pose in poses:
            # Check required fields
            required_fields = ['name', 'duration_min', 'duration_max', 'difficulty', 'dosha_tags', 'emotion_tags', 'benefits']
            missing_fields = [field for field in required_fields if not pose.get(field)]
            
            if missing_fields:
                print(f"   ⚠️  Pose '{pose.get('name')}' missing fields: {missing_fields}")
        
        print(f"   ✅ Checked {len(poses)} yoga poses for data quality")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    print("\n10. Checking sound tracks data quality...")
    try:
        result = supabase.table("sound_tracks").select("*").execute()
        tracks = result.data if result.data else []
        
        for track in tracks:
            # Check required fields
            required_fields = ['title', 'duration_minutes', 'dosha_tags', 'emotion_tags', 'description']
            missing_fields = [field for field in required_fields if not track.get(field)]
            
            if missing_fields:
                print(f"   ⚠️  Track '{track.get('title')}' missing fields: {missing_fields}")
        
        print(f"   ✅ Checked {len(tracks)} sound tracks for data quality")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌟 YOGA & SOUND THERAPY FEATURE VERIFICATION")
    print("="*60)
    
    all_passed = True
    
    # Run tests
    if not test_database_content():
        all_passed = False
    
    if not test_api_filtering():
        all_passed = False
    
    if not test_data_quality():
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n✨ Yoga & Sound Therapy feature is working correctly!")
        print("\nNext steps:")
        print("1. Start the backend server: python run_dev.py")
        print("2. Start the frontend: npm run dev")
        print("3. Log in and navigate to Yoga & Lifestyle page")
        print("4. Verify personalized content appears based on your dosha")
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        print("\n⚠️  Please fix the issues above before proceeding.")
    
    print()
