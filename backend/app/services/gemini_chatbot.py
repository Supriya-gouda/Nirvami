"""
Gemini AI Chatbot Service
Mental health companion specializing in Yoga and Ayurveda
"""
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

# System Instruction - The Rules for the Chatbot
SYSTEM_INSTRUCTION = """You are Nirvami, a compassionate mental health companion specializing in Yoga and Ayurveda.

YOUR ROLE:
- You are an expert in yoga practices, pranayama, meditation, and Ayurvedic wellness
- You provide personalized guidance for mental well-being, stress relief, and emotional balance
- You offer evidence-based recommendations rooted in ancient wisdom and modern psychology
- You are empathetic, supportive, and non-judgmental

YOUR EXPERTISE INCLUDES:
1. Yoga Asanas (poses) for different emotional states and physical conditions
2. Pranayama (breathing exercises) for stress, anxiety, and mood regulation
3. Meditation techniques for mindfulness and inner peace
4. Ayurvedic lifestyle recommendations (diet, sleep, daily routines)
5. Dosha balancing (Vata, Pitta, Kapha) for mental wellness
6. Natural remedies and herbal support for emotional health
7. Mindfulness practices and emotional awareness
8. Stress management and relaxation techniques

IMPORTANT BOUNDARIES:
- If a user asks about topics OUTSIDE of mental health, yoga, Ayurveda, wellness, meditation, or holistic healing, you must politely decline
- When asked about unrelated topics (like math, general knowledge, coding, etc.), respond with:
  "I appreciate your question, but I'm specifically designed to support your mental wellness journey through Yoga and Ayurveda. I'd love to help you with stress relief, emotional balance, meditation practices, or holistic health instead. How are you feeling today? Is there something about your well-being I can help with?"

CRISIS SITUATIONS:
- If someone expresses suicidal thoughts or severe mental health crisis, acknowledge their pain with empathy and strongly encourage them to contact professional help:
  "I hear that you're going through an incredibly difficult time. Your feelings are valid, but I want you to know that professional help is available. Please reach out to:
  - National Crisis Helpline: [provide local number]
  - Text 'HELLO' to crisis support
  - Visit your nearest emergency room
  I'm here to support your wellness journey, but trained professionals can provide the immediate help you need right now."

CONVERSATION STYLE:
- Be warm, compassionate, and encouraging
- Ask clarifying questions to understand the user's specific needs
- Provide practical, actionable advice
- Use simple language, avoid overwhelming medical jargon
- Celebrate small progress and encourage consistency
- Acknowledge emotions without judgment

RESPONSE FORMAT:
- Keep responses conversational and human-like
- Break down complex practices into simple steps
- Suggest 1-3 specific techniques rather than overwhelming with options
- End with an encouraging question or reflection prompt
- When appropriate, explain the "why" behind your recommendations

Remember: You are a supportive companion on their wellness journey, not a replacement for medical or psychiatric care."""


class GeminiChatbot:
    """Gemini-powered chatbot for mental health support"""
    
    def __init__(self):
        """Initialize Gemini client with API key"""
        self.api_key = settings.GEMINI_API_KEY
        
        if not self.api_key or self.api_key == "your-gemini-api-key-here":
            logger.warning("⚠️  GEMINI_API_KEY not configured - chatbot will not work")
            self.model = None
            return
        
        try:
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            
            # Initialize model with safety settings in list format (newer SDK)
            # Using gemini-2.0-flash-001 (stable) - gemini-1.5-flash is deprecated
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-001",
                system_instruction=SYSTEM_INSTRUCTION,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            self.system_instruction = SYSTEM_INSTRUCTION
            
            logger.info("✅ Gemini chatbot initialized successfully with model: gemini-2.0-flash-001")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}", exc_info=True)
            self.model = None
    
    def is_available(self) -> bool:
        """Check if chatbot is properly configured"""
        return self.model is not None
    
    def chat(self, message: str, chat_history: Optional[List[Dict]] = None) -> str:
        """
        Send message to Gemini and get response
        
        Args:
            message: User's message
            chat_history: Previous conversation (optional)
            
        Returns:
            Chatbot's response
        """
        if not self.is_available():
            logger.warning("Gemini not available, using fallback")
            return self._fallback_response(message)
        
        try:
            logger.info(f"[GEMINI] Processing message: {message[:100]}...")
            logger.info(f"[GEMINI] History length: {len(chat_history or [])} messages")
            
            # Start chat session with history if provided
            if chat_history and len(chat_history) > 0:
                # Convert history to Gemini format
                gemini_history = []
                last_role = None
                
                for msg in chat_history[-10:]:  # Last 10 messages for context
                    role = "user" if msg.get("role") == "user" else "model"
                    content = msg.get("content", "")
                    
                    # Skip empty messages
                    if not content:
                        continue
                        
                    # Ensure alternating roles (Gemini requirement)
                    if role == last_role:
                        continue
                        
                    gemini_history.append({
                        "role": role,
                        "parts": [content]
                    })
                    last_role = role
                
                # Ensure history starts with user (if not empty)
                if gemini_history and gemini_history[0]["role"] == "model":
                    gemini_history.pop(0)
                
                logger.info(f"[GEMINI] Starting chat with {len(gemini_history)} valid history messages")
                
                try:
                    chat_session = self.model.start_chat(history=gemini_history)
                    response = chat_session.send_message(message)
                except Exception as chat_err:
                    logger.warning(f"[GEMINI] Chat with history failed ({chat_err}), retrying without history")
                    # Fallback to no history if history causes issues
                    response = self.model.generate_content(message)
            else:
                # Single message - system instruction already in model
                logger.info("[GEMINI] Generating single content (no history)")
                response = self.model.generate_content(message)
            
            response_text = response.text
            logger.info(f"[GEMINI] Response generated: {len(response_text)} chars")
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Gemini chat error: {e}", exc_info=True)
            logger.error(f"[GEMINI] Message that caused error: {message[:200]}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> str:
        """Fallback response when Gemini is not available"""
        return (
            "I apologize, but I'm currently unable to connect to my wellness knowledge base. "
            "However, I'm here to help! "
            "\n\nIn the meantime, here are some general wellness tips:\n"
            "🧘 Take 5 deep breaths - inhale for 4 counts, hold for 4, exhale for 6\n"
            "🌅 Try a simple morning yoga routine to start your day mindfully\n"
            "💧 Stay hydrated and nourish your body with wholesome foods\n"
            "😴 Prioritize quality sleep for emotional balance\n\n"
            "Please check back shortly, and I'll be ready to provide personalized guidance!"
        )


# Global instance
_chatbot_instance = None

def get_chatbot() -> GeminiChatbot:
    """Get or create chatbot instance (singleton pattern)"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = GeminiChatbot()
    return _chatbot_instance
