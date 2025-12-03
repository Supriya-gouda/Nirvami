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


# Emotion to Aura color mapping (shared across endpoints)
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
    "stress": {"color": "indigo", "name": "Stressed Indigo Aura", "traits": ["Tense", "Pressured", "Intense", "Focused"]},
    "disgust": {"color": "green", "name": "Discerning Green Aura", "traits": ["Discerning", "Selective", "Boundary-aware", "Protective"]},
    "surprise": {"color": "orange", "name": "Surprised Orange Aura", "traits": ["Alert", "Responsive", "Aware", "Present"]},
    "neutral": {"color": "grey", "name": "Neutral Grey Aura", "traits": ["Balanced", "Neutral", "Calm", "Centered"]},
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


async def create_aura_entry_from_emotion(user_id: str, emotion_type: str, confidence: float, supabase):
    """Create or update aura_entry based on emotion - REAL-TIME UPDATE.
    
    This function is called IMMEDIATELY when an emotion is logged.
    Uses comprehensive aura mapping system with detailed therapeutic information.
    """
    try:
        from app.services.aura_service import AuraService
        
        # Get aura mapping for the emotion
        emotion_lower = emotion_type.lower()
        aura_key = AuraService.EMOTION_TO_AURA.get(emotion_lower, "neutral")
        aura_info = AuraService.AURA_MAPPINGS[aura_key]
        
        intensity = int(confidence * 100)
        glow_level = min(100, intensity + 20)
        
        # Create comprehensive aura entry
        aura_data = {
            "user_id": user_id,
            "date": date.today().isoformat(),
            "color_code": aura_info["color_code"],
            "intensity": float(intensity),
            "glow_level": float(glow_level),
            "aura_type": aura_key,
            "emotion_basis": {
                "emotion": emotion_type,
                "confidence": confidence,
                "aura_name": aura_info["name"],
                "why": aura_info["why"],
                "what_it_does": aura_info["what_it_does"],
                "purpose": aura_info["purpose"],
                "chakra": aura_info["chakra"],
                "element": aura_info["element"],
                "gradient": aura_info["gradient"]
            },
            "metadata": {
                "created_from": "emotion_log",
                "gradient": aura_info["gradient"],
                "triggered_at": datetime.utcnow().isoformat()
            }
        }
        
        # Upsert (insert or update if exists for this user+date)
        result = supabase.table("aura_entries").upsert(
            aura_data,
            on_conflict="user_id,date"
        ).execute()
        
        logger.info(f"🎨 AURA UPDATED: {aura_info['name']} ({aura_info['color_code']}) for user {user_id}")
        return result.data[0] if result.data else None
        
    except Exception as e:
        logger.error(f"❌ Error creating aura entry: {e}", exc_info=True)
        raise


@router.get("/today")
async def get_today_aura(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get today's aura - generates from emotions if not exists."""
    try:
        supabase = get_supabase(use_service_role=True)
        
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
        supabase = get_supabase(use_service_role=True)
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
    supabase = get_supabase(use_service_role=True)
    
    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()
        
        result = supabase.table("aura_entries").select("*").eq(
            "user_id", current_user_id
        ).gte("date", since_date).order("date", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Error fetching aura timeline: {e}")
        raise


@router.get("/current")
async def get_current_aura(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get the latest aura with comprehensive therapeutic information.
    Updated automatically when user logs emotion.
    """
    from app.services.aura_service import AuraService
    
    supabase = get_supabase(use_service_role=True)
    
    try:
        # Query latest aura entry for this user
        result = supabase.table("aura_entries").select("*").eq(
            "user_id", current_user_id
        ).order("created_at", desc=True).limit(1).execute()
        
        # Return neutral if no aura exists
        if not result.data:
            neutral_info = AuraService.AURA_MAPPINGS["neutral"]
            return {
                "auraName": neutral_info["name"],
                "emotionLabel": "No mood logged yet",
                "colorCode": neutral_info["color_code"],
                "gradient": neutral_info["gradient"],
                "traits": ["Neutral", "Balanced", "Calm", "Stillness"],
                "why": neutral_info["why"],
                "whatItDoes": neutral_info["what_it_does"],
                "purpose": neutral_info["purpose"],
                "chakra": neutral_info["chakra"],
                "element": neutral_info["element"],
                "intensity": 50
            }
        
        # Extract aura data with comprehensive info
        aura = result.data[0]
        emotion_data = aura.get("emotion_basis", {})
        
        return {
            "auraName": emotion_data.get("aura_name", "Neutral Aura"),
            "emotionLabel": emotion_data.get("emotion", "neutral").replace('_', ' ').title(),
            "colorCode": aura["color_code"],
            "gradient": emotion_data.get("gradient", ["#9E9E9E", "#BDBDBD", "#E0E0E0"]),
            "traits": ["Balanced", "Calm"],  # Can be expanded
            "why": emotion_data.get("why", "No data"),
            "whatItDoes": emotion_data.get("what_it_does", "Creates baseline"),
            "purpose": emotion_data.get("purpose", "Hold neutral space"),
            "chakra": emotion_data.get("chakra", "All"),
            "element": emotion_data.get("element", "Earth"),
            "intensity": int(aura.get("intensity", 50))
        }
        
    except Exception as e:
        logger.error(f"Error getting current aura: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/from-latest-emotion")
async def get_aura_from_latest_emotion(
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    DEPRECATED: Use /current endpoint instead.
    Get aura based on the LATEST emotion_logs entry.
    Simple direct mapping: latest emotion -> aura therapy color.
    Returns neutral grey if no emotion or emotion >24h old.
    Also creates/updates aura_entry in database for persistence.
    """
    # Redirect to /current endpoint
    return await get_current_aura(current_user_id)
