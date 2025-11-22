"""Updated chat routes with full emotion detection and database integration."""
from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.schemas import SendMessageRequest, Message, ChatSession, ChatResponse, MessageRole
from app.utils.auth import get_current_user_id
from app.utils.database import get_supabase
from app.services.gemini_chatbot import get_chatbot
from app.services.crisis_detector import CrisisDetector
from app.services.emotion_service import get_emotion_service
from datetime import datetime
from typing import List
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize chatbot
chatbot = get_chatbot()


@router.get("/history")
async def get_chat_history(
    current_user_id: str = Depends(get_current_user_id),
    session_id: str = None,
    limit: int = 50
):
    """Get chat history for the user."""
    supabase = get_supabase()
    
    try:
        query = supabase.table("messages").select("*").eq("user_id", current_user_id)
        
        if session_id:
            query = query.eq("session_id", session_id)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        
        return result.data or []
    except Exception as e:
        logger.error(f"Error getting chat history: {e}", exc_info=True)
        return []


@router.get("/gemini-test")
async def gemini_test():
    """Test endpoint to verify Gemini API is working directly."""
    try:
        if not chatbot.is_available():
            return {
                "ok": False,
                "error": "Chatbot not initialized. Check GEMINI_API_KEY in environment."
            }
        
        logger.info("[TEST] Testing Gemini API directly...")
        response = chatbot.chat("Say 'OK' if you can read this. Respond with just OK.")
        
        return {
            "ok": True,
            "text": response,
            "model_available": chatbot.is_available()
        }
    except Exception as e:
        logger.error(f"[TEST] Gemini test failed: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: Request,
    message_req: SendMessageRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Send a message and get AI response from Gemini chatbot with full emotion detection."""
    logger.info(f"[CHAT] Received message from user {current_user_id}: {message_req.content[:50]}...")
    
    chatbot_available = chatbot.is_available()
    
    if not chatbot_available:
        logger.error("[CHAT] Chatbot not available")
        raise HTTPException(status_code=503, detail="Chatbot service unavailable. Please check GEMINI_API_KEY configuration.")
    
    try:
        supabase = get_supabase()
        
        # Initialize emotion service with model manager if available
        model_manager = getattr(request.app.state, 'model_manager', None)
        emotion_service = get_emotion_service(model_manager)
        
        # Get chat history for context (last 10 messages)
        chat_history = []
        try:
            history_result = supabase.table("messages")\
                .select("*")\
                .eq("user_id", current_user_id)\
                .order("created_at", desc=True)\
                .limit(20)\
                .execute()
            
            if history_result.data:
                # Reverse to get chronological order
                chat_history = [
                    {
                        "role": msg["role"],
                        "content": msg["content"]
                    }
                    for msg in reversed(history_result.data)
                ]
        except Exception as history_error:
            logger.warning(f"Could not load chat history: {history_error}")
        
        # Detect emotion from user message
        emotion_data = emotion_service.detect_emotion(message_req.content)
        logger.info(f"Detected emotion: {emotion_data['emotion_type']} (confidence: {emotion_data['confidence']:.2f})")
        
        # Check for crisis
        is_crisis, severity, triggers = CrisisDetector.detect_crisis(
            message_req.content,
            emotion_data
        )
        
        # Get or create session (Handle DB errors gracefully)
        session_id = message_req.session_id
        try:
            if not session_id:
                session_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": current_user_id,
                    "title": message_req.content[:50],
                    "started_at": datetime.utcnow().isoformat(),
                    "last_message_at": datetime.utcnow().isoformat()
                }
                session_result = supabase.table("chat_sessions").insert(session_data).execute()
                session_id = session_result.data[0]["id"]
            else:
                supabase.table("chat_sessions").update({
                    "last_message_at": datetime.utcnow().isoformat()
                }).eq("id", session_id).execute()
        except Exception as db_err:
            logger.error(f"Database session error: {db_err}")
            # Generate temporary session ID if DB fails
            if not session_id:
                session_id = str(uuid.uuid4())
        
        # Save user message to database (Handle DB errors)
        user_message_id = str(uuid.uuid4())
        user_message_data = {
            "id": user_message_id,
            "session_id": session_id,
            "user_id": current_user_id,
            "role": "user",
            "content": message_req.content,
            "emotion_detected": emotion_data['emotion_type'],
            "emotion_scores": emotion_data['all_scores'],
            "crisis_flag": is_crisis,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            supabase.table("messages").insert(user_message_data).execute()
            
            # Log emotion
            emotion_log = emotion_service.create_emotion_log(
                user_id=current_user_id,
                emotion_type=emotion_data['emotion_type'],
                confidence=emotion_data['confidence'],
                all_scores=emotion_data['all_scores'],
                source='text',
                message_id=user_message_id
            )
            supabase.table("emotion_logs").insert(emotion_log).execute()
        except Exception as db_msg_err:
            logger.error(f"Failed to save user message to DB: {db_msg_err}")
        
        # Handle crisis if detected
        if is_crisis:
            logger.warning(f"🚨 Crisis detected for user {current_user_id}: severity={severity}")
            
            try:
                # Create crisis alert
                alert_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": current_user_id,
                    "alert_type": "crisis",
                    "severity": severity,
                    "title": "Crisis Detection Alert",
                    "message": f"Distress signals detected: {', '.join(triggers)}",
                    "triggered_by": user_message_id,
                    "trigger_metadata": {
                        "triggers": triggers,
                        "emotion": emotion_data['emotion_type'],
                        "message_excerpt": message_req.content[:100]
                    },
                    "status": "active",
                    "notified_channels": ["in_app"],
                    "created_at": datetime.utcnow().isoformat()
                }
                supabase.table("alerts").insert(alert_data).execute()
            except Exception as alert_err:
                logger.error(f"Failed to save crisis alert: {alert_err}")
            
            # Get crisis response
            crisis_response = CrisisDetector.get_crisis_response()
            
            # Return early for crisis
            return ChatResponse(
                message=Message(
                    id=user_message_id,
                    session_id=session_id,
                    user_id=current_user_id,
                    role=MessageRole.USER,
                    content=message_req.content,
                    emotion_detected=emotion_data['emotion_type'],
                    emotion_scores=emotion_data['all_scores'],
                    crisis_flag=True,
                    created_at=datetime.utcnow()
                ),
                response=crisis_response,
                session_id=session_id,
                crisis_detected=True,
                emotion_detected=emotion_data['emotion_type']
            )
        
        # Get response from Gemini chatbot
        logger.info(f"[CHAT] Calling Gemini with message: {message_req.content[:100]}")
        
        try:
            ai_response = chatbot.chat(message_req.content, chat_history)
        except Exception as ai_err:
            logger.error(f"Gemini chat failed completely: {ai_err}")
            ai_response = "I apologize, but I'm having trouble connecting right now. Please try again in a moment."
        
        logger.info(f"[CHAT] ✅ Gemini response: {len(ai_response)} chars")
        
        # Save AI response to database
        ai_message_id = str(uuid.uuid4())
        ai_message_data = {
            "id": ai_message_id,
            "session_id": session_id,
            "user_id": current_user_id,
            "role": "assistant",
            "content": ai_response,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            supabase.table("messages").insert(ai_message_data).execute()
        except Exception as db_ai_err:
            logger.error(f"Failed to save AI response to DB: {db_ai_err}")
        
        # Return response using ChatResponse model
        return ChatResponse(
            message=Message(
                id=user_message_id,
                session_id=session_id,
                user_id=current_user_id,
                role=MessageRole.USER,
                content=message_req.content,
                emotion_detected=emotion_data['emotion_type'],
                emotion_scores=emotion_data['all_scores'],
                crisis_flag=False,
                created_at=datetime.utcnow()
            ),
            response=ai_response,
            session_id=session_id,
            crisis_detected=False,
            emotion_detected=emotion_data['emotion_type']
        )
        
    except Exception as e:
        logger.error(f"❌ Critical error in send_message: {e}", exc_info=True)
        # Even if everything fails, try to return a valid response structure
        return ChatResponse(
            message=Message(
                id=str(uuid.uuid4()),
                session_id=message_req.session_id or str(uuid.uuid4()),
                user_id=current_user_id,
                role=MessageRole.USER,
                content=message_req.content,
                created_at=datetime.utcnow()
            ),
            response="I'm sorry, I encountered a system error. Please try again later.",
            session_id=message_req.session_id or str(uuid.uuid4()),
            crisis_detected=False,
            emotion_detected="neutral"
        )


@router.get("/sessions", response_model=List[ChatSession])
async def get_chat_sessions(
    current_user_id: str = Depends(get_current_user_id),
    limit: int = 20
):
    """Get user's chat sessions."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("chat_sessions").select("*").eq(
            "user_id", current_user_id
        ).order("last_message_at", desc=True).limit(limit).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise


@router.get("/sessions/{session_id}/messages", response_model=List[Message])
async def get_session_messages(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all messages in a session."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("messages").select("*").eq(
            "session_id", session_id
        ).eq("user_id", current_user_id).order("created_at").execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching session messages: {e}")
        raise
