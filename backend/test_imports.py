"""Quick import test."""
print('Testing imports...')
from app.ml.model_manager import ModelManager
from app.services.emotion_service import EmotionService
from app.services.gemini_chatbot import get_chatbot
from app.config import settings

print('✅ All imports successful')
print(f'✅ Gemini API key configured: {bool(settings.GEMINI_API_KEY)}')
print(f'✅ No LLM_MODEL in config: {not hasattr(settings, "LLM_MODEL")}')
print('✅ Backend ready to start!')
