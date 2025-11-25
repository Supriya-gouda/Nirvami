"""
Test script to verify dosha recommendations are coming from database.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.dosha_service import DoshaService
from app.utils.database import get_supabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dosha_service():
    """Test DoshaService fetches recommendations from database."""
    logger.info("="*80)
    logger.info("TESTING DOSHA SERVICE - DATABASE RECOMMENDATIONS")
    logger.info("="*80)
    
    supabase = get_supabase()
    
    # Test each dosha type
    for dosha in ["vata", "pitta", "kapha"]:
        logger.info(f"\n🔍 Testing {dosha.upper()} recommendations...")
        
        # Test diet recommendations
        diet = DoshaService.get_diet_recommendations(dosha, supabase)
        logger.info(f"\n   📋 Diet ({len(diet)} items):")
        for i, rec in enumerate(diet[:3], 1):  # Show first 3
            logger.info(f"      {i}. {rec[:80]}...")
        
        # Test lifestyle recommendations
        lifestyle = DoshaService.get_lifestyle_recommendations(dosha, supabase)
        logger.info(f"\n   🏃 Lifestyle ({len(lifestyle)} items):")
        for i, rec in enumerate(lifestyle[:3], 1):
            logger.info(f"      {i}. {rec[:80]}...")
        
        # Test yoga recommendations
        yoga = DoshaService.get_yoga_recommendations(dosha, supabase)
        logger.info(f"\n   🧘 Yoga ({len(yoga)} items):")
        for i, rec in enumerate(yoga[:3], 1):
            logger.info(f"      {i}. {rec[:80]}...")
    
    logger.info("\n" + "="*80)
    logger.info("✅ TEST COMPLETED!")
    logger.info("="*80)

if __name__ == "__main__":
    test_dosha_service()
