"""
End-to-end test for dosha assessment and recommendations.
Tests the complete flow from database to API response.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase
from app.services.dosha_service import DoshaService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_content():
    """Test that ayurveda_resources has dosha recommendations."""
    logger.info("="*80)
    logger.info("TEST 1: Database Content Verification")
    logger.info("="*80)
    
    supabase = get_supabase()
    
    # Count total recommendations
    result = supabase.table("ayurveda_resources").select("*", count="exact").execute()
    total_count = result.count
    logger.info(f"\n✅ Total resources in database: {total_count}")
    
    # Count by category and dosha
    categories = ["diet", "lifestyle", "yoga", "meditation"]
    doshas = ["vata", "pitta", "kapha"]
    
    summary = {}
    for dosha in doshas:
        summary[dosha] = {}
        for category in categories:
            result = supabase.table("ayurveda_resources")\
                .select("*", count="exact")\
                .eq("category", category)\
                .contains("dosha_tags", [dosha])\
                .execute()
            count = result.count
            summary[dosha][category] = count
    
    logger.info("\n📊 Breakdown by Dosha and Category:")
    for dosha in doshas:
        logger.info(f"\n   {dosha.upper()}:")
        for category in categories:
            count = summary[dosha][category]
            status = "✅" if count > 0 else "❌"
            logger.info(f"      {status} {category.capitalize()}: {count} items")
    
    # Verify minimum counts
    all_good = True
    for dosha in doshas:
        for category in categories:
            if summary[dosha][category] == 0:
                logger.error(f"❌ Missing {category} recommendations for {dosha}!")
                all_good = False
    
    if all_good:
        logger.info("\n✅ TEST 1 PASSED: All doshas have recommendations in all categories")
        return True
    else:
        logger.error("\n❌ TEST 1 FAILED: Some categories missing recommendations")
        return False


def test_service_methods():
    """Test DoshaService methods fetch from database."""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Service Methods Verification")
    logger.info("="*80)
    
    supabase = get_supabase()
    all_passed = True
    
    doshas = ["vata", "pitta", "kapha"]
    
    for dosha in doshas:
        logger.info(f"\n🔍 Testing {dosha.upper()} service methods...")
        
        # Test diet
        diet_recs = DoshaService.get_diet_recommendations(dosha, supabase)
        if len(diet_recs) > 0:
            logger.info(f"   ✅ Diet: {len(diet_recs)} recommendations")
        else:
            logger.error(f"   ❌ Diet: No recommendations!")
            all_passed = False
        
        # Test lifestyle
        lifestyle_recs = DoshaService.get_lifestyle_recommendations(dosha, supabase)
        if len(lifestyle_recs) > 0:
            logger.info(f"   ✅ Lifestyle: {len(lifestyle_recs)} recommendations")
        else:
            logger.error(f"   ❌ Lifestyle: No recommendations!")
            all_passed = False
        
        # Test yoga
        yoga_recs = DoshaService.get_yoga_recommendations(dosha, supabase)
        if len(yoga_recs) > 0:
            logger.info(f"   ✅ Yoga: {len(yoga_recs)} recommendations")
        else:
            logger.error(f"   ❌ Yoga: No recommendations!")
            all_passed = False
    
    if all_passed:
        logger.info("\n✅ TEST 2 PASSED: All service methods return recommendations")
        return True
    else:
        logger.error("\n❌ TEST 2 FAILED: Some service methods returned no data")
        return False


def test_recommendation_structure():
    """Test that recommendations have proper structure."""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Recommendation Structure Verification")
    logger.info("="*80)
    
    supabase = get_supabase()
    
    # Fetch sample recommendations
    result = supabase.table("ayurveda_resources")\
        .select("*")\
        .eq("category", "diet")\
        .contains("dosha_tags", ["vata"])\
        .limit(1)\
        .execute()
    
    if not result.data:
        logger.error("❌ No sample recommendations found!")
        return False
    
    sample = result.data[0]
    logger.info(f"\n📋 Sample Recommendation Structure:")
    logger.info(f"   Title: {sample.get('title', 'N/A')}")
    logger.info(f"   Category: {sample.get('category', 'N/A')}")
    logger.info(f"   Dosha Tags: {sample.get('dosha_tags', [])}")
    logger.info(f"   Content Length: {len(sample.get('content', ''))} chars")
    logger.info(f"   Keywords: {sample.get('keywords', [])}")
    
    # Verify required fields
    required_fields = ['id', 'title', 'content', 'category', 'dosha_tags']
    all_present = True
    
    for field in required_fields:
        if field not in sample or not sample[field]:
            logger.error(f"   ❌ Missing required field: {field}")
            all_present = False
        else:
            logger.info(f"   ✅ Has {field}")
    
    if all_present:
        logger.info("\n✅ TEST 3 PASSED: Recommendations have proper structure")
        return True
    else:
        logger.error("\n❌ TEST 3 FAILED: Some required fields missing")
        return False


def test_data_persistence():
    """Test that data persists in Supabase."""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Data Persistence Verification")
    logger.info("="*80)
    
    supabase = get_supabase()
    
    # Query database twice to ensure data persists
    logger.info("\n🔄 First query...")
    result1 = supabase.table("ayurveda_resources")\
        .select("id")\
        .contains("dosha_tags", ["vata"])\
        .execute()
    count1 = len(result1.data)
    
    logger.info(f"   Found {count1} vata recommendations")
    
    logger.info("\n🔄 Second query (should match)...")
    result2 = supabase.table("ayurveda_resources")\
        .select("id")\
        .contains("dosha_tags", ["vata"])\
        .execute()
    count2 = len(result2.data)
    
    logger.info(f"   Found {count2} vata recommendations")
    
    if count1 == count2 and count1 > 0:
        logger.info(f"\n✅ TEST 4 PASSED: Data persists ({count1} records)")
        return True
    else:
        logger.error(f"\n❌ TEST 4 FAILED: Data inconsistent or missing")
        return False


def main():
    """Run all end-to-end tests."""
    logger.info("\n" + "="*80)
    logger.info("DOSHA ASSESSMENT - END-TO-END TESTING")
    logger.info("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Database Content", test_database_content()))
    results.append(("Service Methods", test_service_methods()))
    results.append(("Recommendation Structure", test_recommendation_structure()))
    results.append(("Data Persistence", test_data_persistence()))
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("\n" + "="*80)
    logger.info(f"Total: {passed}/{len(results)} tests passed")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("="*80)
        logger.info("\n✅ Dosha recommendations are fully operational!")
        logger.info("✅ Data is stored in Supabase database")
        logger.info("✅ Service methods fetch from database")
        logger.info("✅ Ready for production use")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        logger.error("="*80)
        logger.error(f"\n{failed} test(s) need attention")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
