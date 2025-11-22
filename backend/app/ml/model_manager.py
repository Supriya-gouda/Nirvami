"""ML Model Manager - loads and manages all AI models."""
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification,
    pipeline
)
from sentence_transformers import SentenceTransformer
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading and caching of ML models."""
    
    def __init__(self):
        self.embedding_model = None
        self.emotion_model = None
        self.llm_model = None
        self.llm_tokenizer = None
        self.emotion_pipeline = None
        
        # Create cache directory
        os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
    
    async def load_models(self):
        """Load all ML models asynchronously."""
        try:
            await self._load_embedding_model()
            await self._load_emotion_model()
            await self._load_llm_model()
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
        """Load emotion classification model."""
        try:
            logger.info(f"Loading emotion model: {settings.EMOTION_MODEL}")
            self.emotion_pipeline = pipeline(
                "text-classification",
                model=settings.EMOTION_MODEL,
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading emotion model: {e}")
            raise
    
    async def _load_llm_model(self):
        """Load FLAN-T5 model for response generation."""
        try:
            logger.info(f"Loading LLM model: {settings.LLM_MODEL}")
            self.llm_tokenizer = AutoTokenizer.from_pretrained(
                settings.LLM_MODEL,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            self.llm_model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.LLM_MODEL,
                cache_dir=settings.MODEL_CACHE_DIR,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.llm_model = self.llm_model.to("cuda")
            
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
            raise
    
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
    
    def generate_response(
        self,
        prompt: str,
        max_length: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate text response using FLAN-T5.
        
        Args:
            prompt: Input prompt
            max_length: Maximum response length
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text response
        """
        if self.llm_model is None or self.llm_tokenizer is None:
            raise RuntimeError("LLM model not loaded")
        
        # Tokenize input
        inputs = self.llm_tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        
        # Move to same device as model
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = self.llm_model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                num_return_sequences=1
            )
        
        # Decode response
        response = self.llm_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def batch_generate_embeddings(self, texts: list) -> list:
        """Generate embeddings for multiple texts."""
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not loaded")
        
        embeddings = self.embedding_model.encode(texts)
        return [emb.tolist() for emb in embeddings]
