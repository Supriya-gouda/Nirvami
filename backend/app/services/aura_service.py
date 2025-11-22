"""Aura computation service."""
from datetime import date, datetime
from typing import Dict
import uuid
import logging

logger = logging.getLogger(__name__)


class AuraService:
    """Service for generating and managing aura visualizations."""
    
    # Color Therapy Palette (Mental Health + Ayurveda)
    COLOR_THERAPY_PALETTE = {
        "red": {
            "hex": "#E53935",
            "name": "red",
            "keywords": ["energy", "courage", "grounding"],
            "supports": ["lethargy", "lack_of_motivation", "feeling_stuck"],
            "avoid_when": ["high_anxiety", "anger_outburst"],
            "chakra": "root",
            "element": "Fire"
        },
        "orange": {
            "hex": "#FB8C00",
            "name": "orange",
            "keywords": ["joy", "playfulness", "connection"],
            "supports": ["social_isolation", "low_fun", "creative_block"],
            "avoid_when": ["sensory_overload"],
            "chakra": "sacral",
            "element": "Fire"
        },
        "yellow": {
            "hex": "#FDD835",
            "name": "yellow",
            "keywords": ["optimism", "clarity", "confidence"],
            "supports": ["low_mood", "brain_fog"],
            "avoid_when": ["panic", "migraine"],
            "chakra": "solar_plexus",
            "element": "Fire"
        },
        "green": {
            "hex": "#66BB6A",
            "name": "green",
            "keywords": ["balance", "healing", "compassion"],
            "supports": ["burnout_recovery", "emotional_healing"],
            "avoid_when": [],
            "chakra": "heart",
            "element": "Earth"
        },
        "blue": {
            "hex": "#42A5F5",
            "name": "blue",
            "keywords": ["calm", "trust", "communication"],
            "supports": ["stress", "overthinking"],
            "avoid_when": ["emotional_numbness"],
            "chakra": "throat",
            "element": "Water"
        },
        "teal": {
            "hex": "#26A69A",
            "name": "teal",
            "keywords": ["emotional_healing", "safety"],
            "supports": ["vulnerability", "processing_feelings"],
            "avoid_when": [],
            "chakra": "heart_throat_bridge",
            "element": "Water"
        },
        "violet": {
            "hex": "#8E24AA",
            "name": "violet",
            "keywords": ["insight", "intuition", "transformation"],
            "supports": ["big_questions", "meaning_search"],
            "avoid_when": ["disconnected_from_body"],
            "chakra": "third_eye_crown",
            "element": "Ether"
        },
        "pink": {
            "hex": "#EC407A",
            "name": "pink",
            "keywords": ["self_love", "gentleness"],
            "supports": ["self_criticism", "shame", "loneliness"],
            "avoid_when": [],
            "chakra": "heart",
            "element": "Water"
        },
        "white": {
            "hex": "#F5F5F5",
            "name": "white",
            "keywords": ["space", "clarity", "reset"],
            "supports": ["overload", "cluttered_mind"],
            "avoid_when": [],
            "chakra": "all",
            "element": "Light"
        },
        "grey": {
            "hex": "#9E9E9E",
            "name": "grey",
            "keywords": ["neutral", "balance", "stillness"],
            "supports": ["no_data", "baseline"],
            "avoid_when": [],
            "chakra": "all",
            "element": "Earth"
        },
        "indigo": {
            "hex": "#1A237E",
            "name": "indigo",
            "keywords": ["depth", "protection", "containment"],
            "supports": ["heavy_emotions", "deep_reflection"],
            "avoid_when": ["severe_depression"],
            "chakra": "third_eye",
            "element": "Light"
        }
    }
    
    # Emotion to Color Mapping (based on therapeutic principles)
    EMOTION_TO_COLOR = {
        "joy": "orange",
        "happiness": "yellow",
        "love": "pink",
        "excitement": "orange",
        "calm": "teal",
        "sadness": "blue",
        "anger": "red",
        "fear": "indigo",
        "anxiety": "violet",
        "disgust": "green",
        "surprise": "orange",
        "neutral": "grey"
    }
    
    AURA_TYPES = {
        "calm": ["calm", "peace", "relaxed"],
        "energetic": ["joy", "excitement", "happiness"],
        "turbulent": ["anger", "anxiety", "fear"],
        "melancholic": ["sadness", "grief"],
        "balanced": ["neutral", "contentment"]
    }
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def generate_daily_aura(self, user_id: str, target_date: date) -> Dict:
        """
        Generate aura entry for a specific date based on emotions.
        Only falls back to neutral aura if no emotion data exists.
        
        Args:
            user_id: User ID
            target_date: Date to generate aura for
            
        Returns:
            Aura entry data
        """
        try:
            # Get emotion aggregate for the date
            result = self.supabase.table("emotion_aggregates").select("*").eq(
                "user_id", user_id
            ).eq("date", target_date.isoformat()).execute()
            
            if not result.data or len(result.data) == 0:
                # No aggregated emotions, check raw emotion logs
                start_time = datetime.combine(target_date, datetime.min.time())
                end_time = datetime.combine(target_date, datetime.max.time())
                
                raw_emotions = self.supabase.table("emotion_logs").select("*").eq(
                    "user_id", user_id
                ).gte("created_at", start_time.isoformat()).lte(
                    "created_at", end_time.isoformat()
                ).execute()
                
                if not raw_emotions.data or len(raw_emotions.data) == 0:
                    # Truly no emotion data, create neutral aura
                    logger.info(f"No emotion data for {user_id} on {target_date}, creating neutral aura")
                    return await self._create_neutral_aura(user_id, target_date)
                
                # Create temporary aggregate from raw emotions
                emotion_counts = {}
                total_entries = len(raw_emotions.data)
                
                for emotion in raw_emotions.data:
                    etype = emotion["emotion_type"]
                    emotion_counts[etype] = emotion_counts.get(etype, 0) + 1
                
                emotion_dist = {k: v / total_entries for k, v in emotion_counts.items()}
                dominant_emotion = max(emotion_counts, key=emotion_counts.get)
                
                # Calculate valence from emotion distribution
                positive_emotions = ["joy", "happiness", "love", "excitement", "calm", "contentment"]
                negative_emotions = ["sadness", "anger", "fear", "anxiety", "disgust"]
                
                positive_score = sum(emotion_dist.get(e, 0) for e in positive_emotions)
                negative_score = sum(emotion_dist.get(e, 0) for e in negative_emotions)
                total = positive_score + negative_score
                
                average_valence = (positive_score - negative_score) / total if total > 0 else 0
                
                emotion_aggregate = {
                    "emotion_distribution": emotion_dist,
                    "dominant_emotion": dominant_emotion,
                    "average_valence": average_valence,
                    "total_entries": total_entries
                }
            else:
                emotion_aggregate = result.data[0]
            
            emotion_dist = emotion_aggregate.get("emotion_distribution", {})
            dominant_emotion = emotion_aggregate.get("dominant_emotion", "neutral")
            
            # Compute aura properties from REAL emotion data
            color_info = self._compute_aura_color(emotion_dist, dominant_emotion)
            intensity = self._compute_intensity(emotion_dist)
            glow_level = self._compute_glow(emotion_aggregate.get("average_valence", 0))
            aura_type = self._determine_aura_type(emotion_dist)
            
            # Create deterministic aura entry
            aura_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "date": target_date.isoformat(),
                "color": color_info["name"],
                "color_code": color_info["code"],
                "intensity": intensity,
                "glow_level": glow_level,
                "aura_type": aura_type,
                "emotion_basis": emotion_dist,
                "chakra_balance": {},
                "computed_from": {
                    "dominant_emotion": dominant_emotion,
                    "total_entries": emotion_aggregate.get("total_entries", 0),
                    "average_valence": emotion_aggregate.get("average_valence", 0)
                },
                "created_at": date.today().isoformat()
            }
            
            # Upsert aura entry
            result = self.supabase.table("aura_entries").upsert(aura_data).execute()
            
            logger.info(f"Generated aura for {user_id} on {target_date}: {color_info['name']} (intensity: {intensity})")
            
            return result.data[0] if result.data else aura_data
            
        except Exception as e:
            logger.error(f"Error generating aura: {e}")
            # Only fall back to neutral if there's a critical error
            return await self._create_neutral_aura(user_id, target_date)
    
    def _compute_aura_color(self, emotion_dist: Dict[str, float], dominant: str) -> Dict[str, str]:
        """Compute aura color from emotion distribution using color therapy principles."""
        # Get base color from dominant emotion
        color_name = self.EMOTION_TO_COLOR.get(dominant.lower(), "grey")
        color_data = self.COLOR_THERAPY_PALETTE.get(color_name)
        
        if not color_data:
            # Fallback to grey
            color_data = self.COLOR_THERAPY_PALETTE["grey"]
        
        return {
            "name": color_data["name"],
            "code": color_data["hex"]
        }
    
    def _compute_intensity(self, emotion_dist: Dict[str, float]) -> float:
        """Compute aura intensity (0-100)."""
        # Higher intensity for stronger, more concentrated emotions
        if not emotion_dist:
            return 50.0
        
        # Use entropy-like measure
        max_score = max(emotion_dist.values()) if emotion_dist else 0.5
        intensity = max_score * 100
        
        return min(100.0, max(0.0, intensity))
    
    def _compute_glow(self, valence: float) -> float:
        """Compute glow level based on emotional valence."""
        # Positive valence = higher glow
        # Valence ranges from -1 to 1
        glow = ((valence + 1) / 2) * 100  # Normalize to 0-100
        return min(100.0, max(0.0, glow))
    
    def _determine_aura_type(self, emotion_dist: Dict[str, float]) -> str:
        """Determine aura type from emotion distribution."""
        if not emotion_dist:
            return "balanced"
        
        # Check which emotions are present
        present_emotions = [e.lower() for e, score in emotion_dist.items() if score > 0.1]
        
        for aura_type, emotions in self.AURA_TYPES.items():
            if any(e in present_emotions for e in emotions):
                return aura_type
        
        return "balanced"
    
    async def _create_neutral_aura(self, user_id: str, target_date: date) -> Dict:
        """Create a neutral aura entry."""
        grey_color = self.COLOR_THERAPY_PALETTE["grey"]
        aura_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "date": target_date.isoformat(),
            "color": grey_color["name"],
            "color_code": grey_color["hex"],
            "intensity": 50.0,
            "glow_level": 50.0,
            "aura_type": "balanced",
            "emotion_basis": {},
            "chakra_balance": {},
            "computed_from": {"note": "No emotion data available"},
            "created_at": date.today().isoformat()
        }
        
        result = self.supabase.table("aura_entries").upsert(aura_data).execute()
        return result.data[0] if result.data else aura_data
