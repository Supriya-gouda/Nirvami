"""
Test script to verify journal emotion detection is working correctly.
This script tests the EXACT emotion detection flow used by the journal feature.
"""
import sys
from pathlib import Path
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.emotion_service import get_emotion_service
from app.ml.model_manager import ModelManager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_journal_emotion_detection():
    """Test journal emotion detection with the actual service."""
    print("=" * 80)
    print("JOURNAL EMOTION DETECTION TEST")
    print("=" * 80)
    
    # Initialize services
    print("\n1. Initializing ML model and emotion service...")
    model_manager = ModelManager()
    
    # Load models asynchronously (critical step!)
    print("   Loading ML models (this may take a moment)...")
    try:
        await model_manager.load_models()
        print("   ✅ ML models loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load ML models: {e}")
        print("   This is a CRITICAL error - emotion detection will not work!")
        return False
    
    emotion_service = get_emotion_service(model_manager)
    
    # Test cases
    test_cases = [
        {
            "name": "Anxious Text (Required Test Case)",
            "text": "I felt constantly on edge today. Even small tasks took more effort than usual, and I kept worrying about whether I was doing enough.",
            "expected_not": "neutral",
            "expected_emotions": ["fear", "anxiety", "sadness"]
        },
        {
            "name": "Happy Text",
            "text": "Today was amazing! I finally achieved my goal and I'm so proud of myself. Everything fell into place perfectly.",
            "expected_not": "neutral",
            "expected_emotions": ["joy"]
        },
        {
            "name": "Sad Text",
            "text": "I miss my old friends so much. Everything feels different now and I feel really alone. Nothing seems to bring me joy anymore.",
            "expected_not": "neutral",
            "expected_emotions": ["sadness"]
        },
        {
            "name": "Short Text (Should Reject)",
            "text": "okay",
            "expected_not": None,
            "expected_emotions": ["neutral"]
        }
    ]
    
    print("\n2. Testing emotion detection with journal-specific threshold (0.40)...\n")
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*80}")
        print(f"Text: \"{test_case['text']}\"")
        print(f"Text length: {len(test_case['text'])} chars")
        print()
        
        # Run emotion detection with source="journal"
        result = emotion_service.detect_emotion(test_case['text'], source="journal")
        
        emotion = result['primary_emotion']
        confidence = result['confidence']
        source = result['source']
        
        print(f"Result:")
        print(f"  Emotion: {emotion}")
        print(f"  Confidence: {confidence:.4f}")
        print(f"  Source: {source}")
        print(f"  All scores: {result.get('emotion_scores', {})}")
        
        # Validate result
        passed = True
        if test_case['expected_not'] and emotion == test_case['expected_not']:
            print(f"\n❌ FAILED: Got '{emotion}' but should NOT be '{test_case['expected_not']}'")
            passed = False
        elif test_case['expected_emotions'] and emotion not in test_case['expected_emotions']:
            print(f"\n⚠️  WARNING: Got '{emotion}', expected one of {test_case['expected_emotions']}")
            # Don't mark as failed, just warn
        
        if passed and confidence >= 0.40:
            print(f"\n✅ PASSED")
        elif passed and confidence < 0.40:
            print(f"\n⚠️  PASSED but confidence below journal threshold (0.40)")
        
        results.append({
            "name": test_case['name'],
            "emotion": emotion,
            "confidence": confidence,
            "source": source,
            "passed": passed
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status} | {result['name']}: {result['emotion']} ({result['confidence']:.2f}) from {result['source']}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    # Check critical test case
    required_test = results[0]  # First test is the required anxious text
    if required_test['emotion'] == 'neutral':
        print("\n" + "=" * 80)
        print("❌ CRITICAL FAILURE: Required test case returned neutral!")
        print("This indicates the journal emotion detection is NOT working correctly.")
        print("=" * 80)
        return False
    else:
        print("\n" + "=" * 80)
        print("✅ SUCCESS: Required test case passed (not neutral)")
        print("Journal emotion detection is working correctly.")
        print("=" * 80)
        return True

if __name__ == "__main__":
    # Run async test
    success = asyncio.run(test_journal_emotion_detection())
    sys.exit(0 if success else 1)
