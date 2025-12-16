"""
Test script to verify journal emotion detection using DistilRoBERTa.
Tests two different journal texts to ensure different emotions are detected.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ml.model_manager import ModelManager
from app.services.emotion_service import EmotionService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test journal texts
JOURNAL_TEXT_1 = """Today felt overwhelming in the morning. I had so many tasks piling up and I couldn't shake the feeling of anxiety. 
My heart was racing and I felt like I couldn't catch my breath. Everything seemed urgent and I was worried about meeting all the deadlines."""

JOURNAL_TEXT_2 = """I felt mentally tired throughout the day. Even simple tasks required so much effort. 
I couldn't find joy in things that usually make me happy. The day just dragged on and I felt empty and disconnected."""

async def test_emotion_detection():
    """Test emotion detection on two different journal texts."""
    try:
        # Initialize model manager
        logger.info("🔄 Loading ML models...")
        model_manager = ModelManager()
        await model_manager.load_models()
        
        # Get emotion model
        emotion_model = model_manager.get_emotion_model()
        if emotion_model is None:
            logger.error("❌ Emotion model failed to load")
            return
        
        logger.info("✅ Emotion model loaded successfully")
        logger.info("=" * 80)
        
        # Test Journal 1
        logger.info("📝 TESTING JOURNAL 1 (Anxiety/Overwhelm)")
        logger.info(f"Text: {JOURNAL_TEXT_1[:100]}...")
        logger.info(f"Length: {len(JOURNAL_TEXT_1)} characters")
        
        results_1 = emotion_model(JOURNAL_TEXT_1)[0]
        scores_1 = {item['label'].lower(): float(item['score']) for item in results_1}
        top_emotion_1 = max(scores_1, key=scores_1.get)
        top_confidence_1 = scores_1[top_emotion_1]
        
        logger.info(f"🤖 Raw model output: {results_1}")
        logger.info(f"📊 All scores: {scores_1}")
        logger.info(f"🎯 Top emotion: {top_emotion_1} (confidence: {top_confidence_1:.4f})")
        
        logger.info("=" * 80)
        
        # Test Journal 2
        logger.info("📝 TESTING JOURNAL 2 (Sadness/Fatigue)")
        logger.info(f"Text: {JOURNAL_TEXT_2[:100]}...")
        logger.info(f"Length: {len(JOURNAL_TEXT_2)} characters")
        
        results_2 = emotion_model(JOURNAL_TEXT_2)[0]
        scores_2 = {item['label'].lower(): float(item['score']) for item in results_2}
        top_emotion_2 = max(scores_2, key=scores_2.get)
        top_confidence_2 = scores_2[top_emotion_2]
        
        logger.info(f"🤖 Raw model output: {results_2}")
        logger.info(f"📊 All scores: {scores_2}")
        logger.info(f"🎯 Top emotion: {top_emotion_2} (confidence: {top_confidence_2:.4f})")
        
        logger.info("=" * 80)
        
        # Validate results
        logger.info("🔍 VALIDATION RESULTS:")
        
        if top_emotion_1 == top_emotion_2:
            logger.error(f"❌ FAIL: Both texts detected as '{top_emotion_1}' - emotions should differ")
            logger.error(f"   Expected: Different emotions for anxiety vs sadness texts")
        else:
            logger.info(f"✅ PASS: Different emotions detected")
            logger.info(f"   Journal 1: {top_emotion_1} ({top_confidence_1:.4f})")
            logger.info(f"   Journal 2: {top_emotion_2} ({top_confidence_2:.4f})")
        
        if top_confidence_1 == top_confidence_2:
            logger.warning(f"⚠️  WARNING: Identical confidence scores ({top_confidence_1:.4f})")
            logger.warning(f"   This is suspicious - scores should differ")
        else:
            logger.info(f"✅ PASS: Different confidence scores")
        
        if top_emotion_1 == 'neutral' and top_emotion_2 == 'neutral':
            logger.error(f"❌ FAIL: Both texts defaulted to 'neutral' - model not being used properly")
        else:
            logger.info(f"✅ PASS: No inappropriate defaults")
        
        logger.info("=" * 80)
        logger.info("✅ Test completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        logger.exception(e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_emotion_detection())
