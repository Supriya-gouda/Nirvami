#!/usr/bin/env python3
"""
Quick test to check existing data and populate if needed
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.database import get_supabase

async def check_and_populate_data():
    """Check existing data and populate if needed"""
    try:
        supabase = get_supabase()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check for existing recommendations
        existing = supabase.table('recommendations').select('*').limit(5).execute()
        
        if existing.data:
            print(f"✅ Found {len(existing.data)} existing recommendations")
            for rec in existing.data:
                print(f"   - [{rec['category']}] {rec['title']} (by {rec['user_id']})")
            
            # Get the first user ID for testing
            test_user_id = existing.data[0]['user_id']
            print(f"\n🧪 Using user ID for testing: {test_user_id}")
            
            # Check today's recommendations for this user
            today_recs = supabase.table('recommendations')\
                .select('*')\
                .eq('user_id', test_user_id)\
                .eq('date', today)\
                .execute()
            
            print(f"📅 Today's recommendations for {test_user_id}: {len(today_recs.data)}")
            
            if today_recs.data:
                for rec in today_recs.data:
                    print(f"   - [{rec['category']}] {rec['title']} from {rec['source']}")
            else:
                print("   No recommendations for today - creating some...")
                
                # Create sample recommendations for today
                sample_recs = [
                    {
                        'user_id': test_user_id,
                        'content': 'Practice Child\'s Pose (Balasana) to release tension in your lower back and promote relaxation.',
                        'title': 'Child\'s Pose for Lower Back Relief',
                        'category': 'yoga',
                        'source': 'chat',
                        'confidence_score': 0.95,
                        'date': today,
                        'created_at': datetime.now().isoformat()
                    },
                    {
                        'user_id': test_user_id,
                        'content': 'Based on your heart rate patterns, try gentle breathing exercises to reduce stress.',
                        'title': 'Breathing Exercises for Stress Relief',
                        'category': 'yoga',
                        'source': 'device',
                        'confidence_score': 0.88,
                        'date': today,
                        'created_at': datetime.now().isoformat()
                    },
                    {
                        'user_id': test_user_id,
                        'content': 'Follow a Vata-pacifying routine with warm foods and regular meal times.',
                        'title': 'Vata-Pacifying Daily Routine',
                        'category': 'ayurveda',
                        'source': 'chat',
                        'confidence_score': 0.90,
                        'date': today,
                        'created_at': datetime.now().isoformat()
                    }
                ]
                
                result = supabase.table('recommendations').insert(sample_recs).execute()
                if result.data:
                    print(f"✅ Created {len(result.data)} sample recommendations for today")
                
        else:
            print("❌ No existing recommendations found")
            print("ℹ️  Run the chat or device integration first to populate data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_populate_data())