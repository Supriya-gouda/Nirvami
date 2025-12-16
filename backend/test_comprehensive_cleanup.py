"""
Comprehensive Test: Verify Flan-T5 Removal and System Functionality
Tests all critical features to ensure nothing broke after cleanup
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ml.model_manager import ModelManager
from app.services.emotion_service import EmotionService
from app.services.gemini_chatbot import get_chatbot
import logging

logging.basicConfig(level=logging.WARNING)  # Reduce noise

async def run_comprehensive_tests():
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE POST-CLEANUP TESTS")
    print("="*80)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Model Manager Initialization
    print("\n[1/6] Testing Model Manager Initialization...")
    try:
        manager = ModelManager()
        await manager.load_models()
        assert manager.embedding_model is not None
        assert manager.emotion_pipeline is not None
        assert not hasattr(manager, 'llm_model')
        assert not hasattr(manager, 'llm_tokenizer')
        assert not hasattr(manager, 'generate_response')
        print("   ✅ PASS: Model manager loads without Flan-T5")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 2: Embedding Generation
    print("\n[2/6] Testing Embedding Generation...")
    try:
        text = "Test embedding generation"
        embedding = manager.generate_embedding(text)
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # MiniLM dimension
        print(f"   ✅ PASS: Generated {len(embedding)}-dim embedding")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 3: Emotion Detection
    print("\n[3/6] Testing Emotion Detection...")
    try:
        emotion_service = EmotionService(manager)
        result = emotion_service.detect_emotion("I'm so happy today!")
        assert result['primary_emotion'] == 'joy'
        assert result['confidence'] > 0.5
        assert result['source'] == 'ml'
        print(f"   ✅ PASS: Detected '{result['primary_emotion']}' with {result['confidence']:.2%} confidence")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 4: Contextual Emotion Detection
    print("\n[4/6] Testing Contextual Emotion Detection...")
    try:
        messages = [
            "I had a terrible day",
            "Everything went wrong",
            "I feel so frustrated"
        ]
        result = emotion_service.detect_contextual_emotion(messages)
        assert result['primary_emotion'] in ['sadness', 'anger', 'fear']
        assert result['confidence'] > 0.5
        print(f"   ✅ PASS: Context detected '{result['primary_emotion']}' emotion")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 5: Gemini Chatbot Initialization
    print("\n[5/6] Testing Gemini Chatbot...")
    try:
        chatbot = get_chatbot()
        assert chatbot.is_available() == True
        assert chatbot.model is not None
        print("   ✅ PASS: Gemini chatbot initialized successfully")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 6: Configuration Check
    print("\n[6/6] Testing Configuration...")
    try:
        from app.config import settings
        assert hasattr(settings, 'EMBEDDING_MODEL')
        assert hasattr(settings, 'EMOTION_MODEL')
        assert not hasattr(settings, 'LLM_MODEL')
        assert settings.GEMINI_API_KEY is not None
        print("   ✅ PASS: Configuration updated correctly")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Tests Passed: {tests_passed}/6")
    print(f"Tests Failed: {tests_failed}/6")
    
    if tests_failed == 0:
        print("\n✅ ALL TESTS PASSED - FLAN-T5 SUCCESSFULLY REMOVED!")
        print("\n🎯 System Status:")
        print("   ✓ Model Manager: Clean (no Flan-T5)")
        print("   ✓ Emotion Detection: Working (ML-first)")
        print("   ✓ Embeddings: Working (MiniLM)")
        print("   ✓ Gemini Chatbot: Working")
        print("   ✓ Configuration: Updated")
        print("\n🎉 Ready for production!")
    else:
        print(f"\n❌ {tests_failed} TEST(S) FAILED - REVIEW REQUIRED")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
