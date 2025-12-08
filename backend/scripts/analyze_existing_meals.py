"""Analyze existing meals for a specific user."""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase
from app.services.meal_service import meal_service

async def analyze_user_meals(user_email: str):
    """Analyze all existing meals for a user"""
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Get user ID from email
        user_result = supabase.table('profiles').select('id').eq('email', user_email).execute()
        
        if not user_result.data:
            print(f"❌ User not found: {user_email}")
            return
        
        user_id = user_result.data[0]['id']
        print(f"✅ Found user: {user_email} (ID: {user_id})")
        
        # Get all meals for this user
        meals_result = supabase.table('meals').select('*').eq('user_id', user_id).order('meal_time', desc=True).execute()
        
        if not meals_result.data:
            print(f"❌ No meals found for user {user_email}")
            return
        
        meals = meals_result.data
        print(f"📊 Found {len(meals)} meals to analyze\n")
        
        # Analyze each meal
        for i, meal in enumerate(meals, 1):
            print(f"Analyzing meal {i}/{len(meals)}: {meal['meal_text'][:50]}...")
            
            try:
                # Generate comprehensive analysis
                analysis = await meal_service._perform_comprehensive_meal_analysis(
                    user_id,
                    meal['id'],
                    meal['meal_text'],
                    meal.get('ingredients', []),
                    meal.get('dosha_impact_tags', {})
                )
                
                print(f"  ✅ Analysis complete")
                print(f"     Health Score: {analysis.get('health_assessment', {}).get('health_score', 'N/A')}/100")
                print(f"     Is Healthy: {analysis.get('health_assessment', {}).get('is_healthy', 'N/A')}")
                
                # Generate guidelines for this meal
                await meal_service._generate_daily_guidelines(user_id, meal['id'])
                print(f"  ✅ Guidelines generated")
                
                # Create mood-meal correlation
                await meal_service._create_mood_meal_correlation(user_id, meal['id'])
                print(f"  ✅ Mood correlation created\n")
                
            except Exception as e:
                print(f"  ❌ Error analyzing meal: {e}\n")
        
        print(f"\n🎉 Analysis complete for {len(meals)} meals!")
        print(f"\nGuidelines and correlations have been generated.")
        print(f"User can now see analysis in the Diet & Mood Sync page.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    user_email = "test.user@nirvami.com"
    if len(sys.argv) > 1:
        user_email = sys.argv[1]
    
    print(f"🔄 Analyzing meals for: {user_email}\n")
    asyncio.run(analyze_user_meals(user_email))
