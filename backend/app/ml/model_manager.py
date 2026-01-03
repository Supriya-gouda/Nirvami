"""ML Model Manager - loads and manages AI models for embeddings and emotion detection."""
import torch
from transformers import (
    AutoModelForSequenceClassification,
    pipeline
)
from sentence_transformers import SentenceTransformer
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading and caching of ML models (embeddings and emotion detection)."""
    
    def __init__(self):
        self.embedding_model = None
        self.emotion_model = None
        self.emotion_pipeline = None
        
        # Create cache directory
        os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
    
    async def load_models(self):
        """Load ML models asynchronously."""
        try:
            await self._load_embedding_model()
            await self._load_emotion_model()
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    async def _load_embedding_model(self):
        """Load sentence transformer for embeddings."""
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                cache_folder=settings.MODEL_CACHE_DIR
            )
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    async def _load_emotion_model(self):
        """Load emotion classification model (go_emotions)."""
        try:
            logger.info(f"[MODEL] Loading go_emotions model: {settings.EMOTION_MODEL}")
            self.emotion_pipeline = pipeline(
                "text-classification",
                model=settings.EMOTION_MODEL,
                top_k=None,  # Return all scores for go_emotions
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("[MODEL] Loaded go_emotions model successfully")
        except Exception as e:
            logger.error(f"Error loading emotion model: {e}")
            raise
    
    def get_embedding_model(self):
        """Get sentence transformer model (lazy-loaded and cached)."""
        return self.embedding_model
    
    def get_emotion_model(self):
        """Get emotion classification pipeline (lazy-loaded and cached)."""
        return self.emotion_pipeline
    
    def generate_embedding(self, text: str) -> list:
        """
        Generate embedding vector for text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not loaded")
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def detect_emotion(self, text: str) -> dict:
        """
        Detect emotion from text.
        
        Args:
            text: Input text
            
        Returns:
            Dict with emotion scores
        """
        if self.emotion_pipeline is None:
            raise RuntimeError("Emotion model not loaded")
        
        results = self.emotion_pipeline(text)[0]
        
        # Convert to dict
        emotion_scores = {item['label']: item['score'] for item in results}
        
        # Get dominant emotion
        dominant = max(results, key=lambda x: x['score'])
        
        return {
            "dominant_emotion": dominant['label'],
            "confidence": dominant['score'],
            "all_scores": emotion_scores
        }
    
    def batch_generate_embeddings(self, texts: list) -> list:
        """Generate embeddings for multiple texts."""
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not loaded")
        
        embeddings = self.embedding_model.encode(texts)
        return [emb.tolist() for emb in embeddings]
