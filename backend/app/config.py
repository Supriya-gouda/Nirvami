"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_MESSAGING_SERVICE_SID: str = ""
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@nirvami.app"
    
    # Google Gemini API
    GEMINI_API_KEY: str
    
    # YouTube API
    YOUTUBE_API_KEY: str = ""
    
    # Application
    SECRET_KEY: str
    API_VERSION: str = "v1"
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # ML Models (Embeddings and Emotion Detection)
    # Note: Local LLM (Flan-T5) was deprecated - using Gemini API for text generation
    MODEL_CACHE_DIR: str = "./models_cache"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMOTION_MODEL: str = "SamLowe/roberta-base-go_emotions"
    
    # Features
    ENABLE_VOICE_EMOTION: bool = False
    CRISIS_ALERT_ENABLED: bool = True
    ENABLE_ML_MODELS: bool = True  # Enable ML models for production
    USE_MOCK_DATA: bool = False  # Use real database
    
    # Emotion Detection Settings
    USE_ML_EMOTION_MODEL: bool = True  # Use ML model for emotion detection (fallback to rules if fails)
    EMOTION_CONFIDENCE_THRESHOLD: float = 0.45  # Min confidence to use ML result, else fallback to rules
    
    @property
    def origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
