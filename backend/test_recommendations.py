"""
Test script to verify recommendation system is working
"""
import logging
import asyncio
from datetime import datetime, date
from app.services.recommendation_service import recommendation_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_recommendation_extraction():
    """Test the recommendation extraction and storage"""
    
    # Test message with clear recommendations
    test_message = """
    Here are some suggestions to help with stress and anxiety:

    **Yoga Practices:**
    - Try the Child's Pose (Balasana) for 2-3 minutes to ground yourself
    - Practice gentle Sun Salutations in the morning
    - Consider doing legs-up-the-wall pose before bed

    **Breathing Techniques:**
    - Practice 4-7-8 breathing: inhale for 4, hold for 7, exhale for 8
    - Try alternate nostril breathing (Nadi Shodhana) for 5-10 minutes

    **Ayurvedic Lifestyle:**
    - Start your day with warm water and lemon
    - Try drinking calming herbal teas like chamomile or ashwagandha
    - Establish a regular sleep routine, going to bed by 10 PM
    """
    
    test_user_id = "test-user-123"
    
    try:
        logger.info("Testing recommendation extraction...")
        
        # Test extraction
        recommendations = await recommendation_service.extract_and_store_recommendations_from_chat(
            user_id=test_user_id,
            message_text=test_message,
            timestamp=datetime.now()
        )
        
        logger.info(f"✅ Extracted {len(recommendations)} recommendations")
        for rec in recommendations:
            logger.info(f"   - {rec.category}: {rec.title}")
        
        # Test retrieval
        logger.info("Testing recommendation retrieval...")
        
        yoga_recs = await recommendation_service.get_recommendations_by_category(
            user_id=test_user_id,
            category="yoga",
            target_date=date.today()
        )
        logger.info(f"✅ Retrieved {len(yoga_recs)} yoga recommendations")
        
        daily_recs = await recommendation_service.get_daily_recommendations(
            user_id=test_user_id,
            target_date=date.today()
        )
        
        total_recs = sum([
            len(daily_recs.yoga),
            len(daily_recs.ayurveda),
            len(daily_recs.lifestyle),
            len(daily_recs.breathing),
            len(daily_recs.meditation),
            len(daily_recs.diet),
            len(daily_recs.sleep)
        ])
        logger.info(f"✅ Total daily recommendations: {total_recs}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_recommendation_extraction())
    if success:
        print("🎉 Recommendation system test passed!")
    else:
        print("💥 Recommendation system test failed!")