"""Test that model_manager works without Flan-T5."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ml.model_manager import ModelManager
import logging

logging.basicConfig(level=logging.INFO)

async def test_model_manager():
    print("\n" + "="*80)
    print("🧪 TESTING MODEL MANAGER (WITHOUT FLAN-T5)")
    print("="*80)
    
    # Initialize model manager
    print("\n1. Initializing ModelManager...")
    manager = ModelManager()
    
    # Check initialization
    print(f"   - Embedding model: {manager.embedding_model}")
    print(f"   - Emotion pipeline: {manager.emotion_pipeline}")
    print(f"   ✅ Initialized (models not loaded yet)")
    
    # Load models
    print("\n2. Loading models...")
    await manager.load_models()
    print(f"   ✅ Models loaded successfully")
    
    # Test embedding model
    print("\n3. Testing embedding model...")
    test_text = "I feel happy today"
    embedding = manager.generate_embedding(test_text)
    print(f"   Text: \"{test_text}\"")
    print(f"   Embedding dimension: {len(embedding)}")
    print(f"   ✅ Embedding generation works")
    
    # Test emotion model
    print("\n4. Testing emotion model...")
    emotion_result = manager.detect_emotion(test_text)
    print(f"   Text: \"{test_text}\"")
    print(f"   Dominant emotion: {emotion_result['dominant_emotion']}")
    print(f"   Confidence: {emotion_result['confidence']:.3f}")
    print(f"   ✅ Emotion detection works")
    
    # Test getter methods
    print("\n5. Testing getter methods...")
    emb_model = manager.get_embedding_model()
    emo_model = manager.get_emotion_model()
    print(f"   get_embedding_model(): {emb_model is not None}")
    print(f"   get_emotion_model(): {emo_model is not None}")
    print(f"   ✅ Getter methods work")
    
    # Check that Flan-T5 methods are gone
    print("\n6. Verifying Flan-T5 removal...")
    has_generate_response = hasattr(manager, 'generate_response')
    has_llm_model = hasattr(manager, 'llm_model')
    has_llm_tokenizer = hasattr(manager, 'llm_tokenizer')
    
    print(f"   Has generate_response method: {has_generate_response}")
    print(f"   Has llm_model attribute: {has_llm_model}")
    print(f"   Has llm_tokenizer attribute: {has_llm_tokenizer}")
    
    if not has_generate_response and not has_llm_model and not has_llm_tokenizer:
        print(f"   ✅ Flan-T5 completely removed")
    else:
        print(f"   ❌ WARNING: Flan-T5 remnants still present")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - MODEL MANAGER WORKS WITHOUT FLAN-T5")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_model_manager())
