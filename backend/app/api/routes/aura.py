"""Aura visualization routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_current_user_id
from app.models.schemas import AuraEntry
from app.services.aura_service import AuraService
from app.utils.database import get_supabase
from typing import List, Dict, Any
from datetime import date, timedelta, datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/today")
async def get_today_aura(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get today's aura - generates from emotions if not exists."""
    try:
        supabase = get_supabase()
        
        # Try to get existing aura for today
        result = supabase.table("aura_entries").select("*").eq(
            "user_id", current_user_id
        ).eq("date", date.today().isoformat()).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        # If no aura exists, generate one based on real emotion data
        aura_service = AuraService(supabase)
        aura_data = await aura_service.generate_daily_aura(current_user_id, date.today())
        return aura_data
        
    except Exception as e:
        logger.error(f"Error fetching today's aura: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch aura: {str(e)}")


@router.post("/generate")
async def generate_aura(
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate/regenerate today's aura based on recent emotions."""
    try:
        supabase = get_supabase()
        aura_service = AuraService(supabase)
        
        # Generate aura for today
        aura_data = await aura_service.generate_daily_aura(current_user_id, date.today())
        
        return aura_data
    except Exception as e:
        logger.error(f"Error generating aura: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate aura: {str(e)}")


@router.get("/timeline", response_model=List[AuraEntry])
async def get_aura_timeline(
    current_user_id: str = Depends(get_current_user_id),
    days: int = 30
):
    """Get aura timeline."""
    supabase = get_supabase()
    
    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = supabase.table("aura_entries").select("*").eq(
            "user_id", current_user_id
        ).gte("date", since_date).order("date", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching aura timeline: {e}")
        raise


@router.get("/from-latest-emotion")
async def get_aura_from_latest_emotion(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get aura based on the LATEST emotion_logs entry.
    Simple direct mapping: latest emotion -> aura therapy color.
    Returns neutral grey if no emotion or emotion >24h old.
    """
    supabase = get_supabase()
    
    try:
        # Get latest emotion from emotion_logs for this user
        result = supabase.table("emotion_logs").select("*").eq(
            "user_id", current_user_id
        ).order("created_at", desc=True).limit(1).execute()
        
        # Emotion to Aura Therapy mapping
        EMOTION_TO_AURA = {
            # Core emotions
            "joy": {"color": "yellow", "name": "Joyful Yellow Aura", "traits": ["Joyful", "Happy", "Bright", "Optimistic"]},
            "happiness": {"color": "yellow", "name": "Happy Yellow Aura", "traits": ["Happy", "Cheerful", "Warm", "Positive"]},
            "love": {"color": "pink", "name": "Loving Pink Aura", "traits": ["Loving", "Gentle", "Compassionate", "Nurturing"]},
            "excitement": {"color": "orange", "name": "Excited Orange Aura", "traits": ["Excited", "Energetic", "Playful", "Dynamic"]},
            "calm": {"color": "blue", "name": "Calm Blue Aura", "traits": ["Calm", "Peaceful", "Tranquil", "Serene"]},
            "sadness": {"color": "indigo", "name": "Melancholic Indigo Aura", "traits": ["Reflective", "Deep", "Processing", "Introspective"]},
            "anger": {"color": "red", "name": "Intense Red Aura", "traits": ["Powerful", "Intense", "Passionate", "Strong"]},
            "fear": {"color": "indigo", "name": "Protective Indigo Aura", "traits": ["Cautious", "Protected", "Aware", "Alert"]},
            "anxiety": {"color": "indigo", "name": "Anxious Indigo Aura", "traits": ["Tense", "Uncertain", "Alert", "Vigilant"]},
            "disgust": {"color": "green", "name": "Discerning Green Aura", "traits": ["Discerning", "Selective", "Boundary-aware", "Protective"]},
            "surprise": {"color": "orange", "name": "Surprised Orange Aura", "traits": ["Alert", "Responsive", "Aware", "Present"]},
            "neutral": {"color": "grey", "name": "Neutral Grey Aura", "traits": ["Balanced", "Neutral", "Calm", "Centered"]},
            
            # 15 Mental States
            "balanced": {"color": "green", "name": "Balanced Green Aura", "traits": ["Balanced", "Harmonious", "Stable", "Grounded"]},
            "balanced & calm": {"color": "green", "name": "Balanced Green-Blue Aura", "traits": ["Balanced", "Calm", "Harmonious", "Peaceful"]},
            "energized": {"color": "orange", "name": "Energized Orange Aura", "traits": ["Energetic", "Active", "Vibrant", "Dynamic"]},
            "energized & active": {"color": "orange", "name": "Energized Orange-Red Aura", "traits": ["Energized", "Active", "Motivated", "Strong"]},
            "stressed": {"color": "indigo", "name": "Stressed Indigo Aura", "traits": ["Tense", "Pressured", "Intense", "Focused"]},
            "stressed & anxious": {"color": "indigo", "name": "Stressed Dark Aura", "traits": ["Stressed", "Anxious", "Tense", "Overwhelmed"]},
            "focused": {"color": "purple", "name": "Focused Violet Aura", "traits": ["Focused", "Sharp", "Clear", "Concentrated"]},
            "focused & sharp": {"color": "purple", "name": "Focused Violet Aura", "traits": ["Focused", "Sharp", "Precise", "Concentrated"]},
            "tired": {"color": "blue", "name": "Tired Blue Aura", "traits": ["Tired", "Drained", "Resting", "Recovering"]},
            "tired & drained": {"color": "blue", "name": "Fatigued Blue Aura", "traits": ["Tired", "Drained", "Low-energy", "Depleted"]},
            "joyful": {"color": "yellow", "name": "Joyful Yellow Aura", "traits": ["Joyful", "Happy", "Radiant", "Uplifted"]},
            "joyful & happy": {"color": "yellow", "name": "Joyful Golden Aura", "traits": ["Joyful", "Happy", "Bright", "Radiant"]},
            "sad": {"color": "indigo", "name": "Sad Indigo Aura", "traits": ["Sad", "Reflective", "Processing", "Deep"]},
            "sad & low": {"color": "indigo", "name": "Low Indigo Aura", "traits": ["Sad", "Low", "Melancholic", "Introspective"]},
            "frustrated": {"color": "red", "name": "Frustrated Red Aura", "traits": ["Frustrated", "Intense", "Challenged", "Determined"]},
            "angry & frustrated": {"color": "red", "name": "Intense Red Aura", "traits": ["Angry", "Frustrated", "Intense", "Powerful"]},
            "peaceful": {"color": "blue", "name": "Peaceful Blue-White Aura", "traits": ["Peaceful", "Content", "Serene", "Tranquil"]},
            "peaceful & content": {"color": "blue", "name": "Peaceful White-Blue Aura", "traits": ["Peaceful", "Content", "Satisfied", "Harmonious"]},
            "confused": {"color": "grey", "name": "Confused Grey Aura", "traits": ["Confused", "Uncertain", "Searching", "Questioning"]},
            "confused & uncertain": {"color": "grey", "name": "Uncertain Grey Aura", "traits": ["Confused", "Uncertain", "Seeking", "Processing"]},
            "motivated": {"color": "red", "name": "Motivated Red Aura", "traits": ["Motivated", "Driven", "Determined", "Ambitious"]},
            "motivated & driven": {"color": "red", "name": "Driven Red-Gold Aura", "traits": ["Motivated", "Driven", "Goal-oriented", "Powerful"]},
            "overwhelmed": {"color": "indigo", "name": "Overwhelmed Dark Aura", "traits": ["Overwhelmed", "Heavy", "Burdened", "Pressured"]},
            "creative": {"color": "purple", "name": "Creative Violet Aura", "traits": ["Creative", "Inspired", "Artistic", "Innovative"]},
            "creative & inspired": {"color": "purple", "name": "Creative Violet-Orange Aura", "traits": ["Creative", "Inspired", "Artistic", "Visionary"]},
            "restless": {"color": "red", "name": "Restless Red Aura", "traits": ["Restless", "Agitated", "Active", "Stirring"]},
            "restless & agitated": {"color": "red", "name": "Agitated Red-Orange Aura", "traits": ["Restless", "Agitated", "Intense", "Unsettled"]},
            "grateful": {"color": "pink", "name": "Grateful Pink Aura", "traits": ["Grateful", "Thankful", "Appreciative", "Warm"]},
            "grateful & thankful": {"color": "pink", "name": "Grateful Pink-White Aura", "traits": ["Grateful", "Thankful", "Blessed", "Appreciative"]},
        }
        
        # Aura color definitions with gradients
        AURA_COLORS = {
            "red": {
                "gradient": ["#f87171", "#ef4444", "#dc2626"],
                "chakra": "Root Chakra",
                "element": "Fire",
                "description": "Grounded energy, vitality, and courage"
            },
            "orange": {
                "gradient": ["#fb923c", "#f97316", "#ea580c"],
                "chakra": "Sacral Chakra",
                "element": "Fire",
                "description": "Creativity, joy, and emotional flow"
            },
            "yellow": {
                "gradient": ["#facc15", "#eab308", "#ca8a04"],
                "chakra": "Solar Plexus Chakra",
                "element": "Fire",
                "description": "Personal power, confidence, and optimism"
            },
            "green": {
                "gradient": ["#4ade80", "#22c55e", "#16a34a"],
                "chakra": "Heart Chakra",
                "element": "Earth",
                "description": "Love, compassion, and balance"
            },
            "blue": {
                "gradient": ["#60a5fa", "#3b82f6", "#2563eb"],
                "chakra": "Throat Chakra",
                "element": "Water",
                "description": "Communication, calm, and truth"
            },
            "indigo": {
                "gradient": ["#818cf8", "#6366f1", "#4f46e5"],
                "chakra": "Third Eye Chakra",
                "element": "Light",
                "description": "Intuition, depth, and protection"
            },
            "purple": {
                "gradient": ["#a78bfa", "#8b5cf6", "#7c3aed"],
                "chakra": "Crown Chakra",
                "element": "Ether",
                "description": "Spiritual awareness and transformation"
            },
            "pink": {
                "gradient": ["#f472b6", "#ec4899", "#db2777"],
                "chakra": "Heart Chakra",
                "element": "Water",
                "description": "Self-love, gentleness, and compassion"
            },
            "grey": {
                "gradient": ["#9ca3af", "#6b7280", "#4b5563"],
                "chakra": "All Chakras",
                "element": "Earth",
                "description": "Neutral, balanced, and centered"
            }
        }
        
        # Check if we have an emotion and if it's recent (within 24 hours)
        if not result.data or len(result.data) == 0:
            # No emotion at all -> return neutral grey aura
            logger.info(f"No emotions found for user {current_user_id}, returning neutral aura")
            return {
                "auraName": "Neutral Grey Aura",
                "emotionLabel": "No recent mood logged",
                "colorCode": "grey",
                "gradient": AURA_COLORS["grey"]["gradient"],
                "traits": ["Neutral", "Balanced", "Calm", "Stillness"],
                "description": AURA_COLORS["grey"]["description"],
                "chakra": AURA_COLORS["grey"]["chakra"],
                "element": AURA_COLORS["grey"]["element"],
                "intensity": 50
            }
        
        latest_emotion = result.data[0]
        created_at = datetime.fromisoformat(latest_emotion["created_at"].replace('Z', '+00:00'))
        now = datetime.now(created_at.tzinfo)
        
        # Check if emotion is older than 24 hours
        if (now - created_at) > timedelta(hours=24):
            logger.info(f"Latest emotion for user {current_user_id} is >24h old, returning neutral aura")
            return {
                "auraName": "Neutral Grey Aura",
                "emotionLabel": "No recent mood (>24h)",
                "colorCode": "grey",
                "gradient": AURA_COLORS["grey"]["gradient"],
                "traits": ["Neutral", "Balanced", "Calm", "Stillness"],
                "description": AURA_COLORS["grey"]["description"],
                "chakra": AURA_COLORS["grey"]["chakra"],
                "element": AURA_COLORS["grey"]["element"],
                "intensity": 50
            }
        
        # We have a recent emotion - map it to aura
        emotion_type = latest_emotion["emotion_type"].lower()
        confidence = latest_emotion.get("confidence", 0.5)
        
        # Get aura mapping or default to neutral
        aura_mapping = EMOTION_TO_AURA.get(emotion_type, EMOTION_TO_AURA["neutral"])
        color_code = aura_mapping["color"]
        color_info = AURA_COLORS[color_code]
        
        logger.info(f"Mapped emotion '{emotion_type}' to aura color '{color_code}' for user {current_user_id}")
        
        return {
            "auraName": aura_mapping["name"],
            "emotionLabel": emotion_type.replace('_', ' ').title(),
            "colorCode": color_code,
            "gradient": color_info["gradient"],
            "traits": aura_mapping["traits"],
            "description": color_info["description"],
            "chakra": color_info["chakra"],
            "element": color_info["element"],
            "intensity": int(confidence * 100)  # Convert 0-1 confidence to 0-100 intensity
        }
        
    except Exception as e:
        logger.error(f"Error getting aura from latest emotion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get aura: {str(e)}")
