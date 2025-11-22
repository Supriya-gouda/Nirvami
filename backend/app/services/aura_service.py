"""Aura computation service."""
from datetime import date, datetime
from typing import Dict
import uuid
import logging

logger = logging.getLogger(__name__)


class AuraService:
    """Service for generating and managing aura visualizations."""
    
    # Emotion to color mapping
    EMOTION_COLORS = {
        "joy": {"code": "#FFD700", "name": "yellow"},  # Gold
        "happiness": {"code": "#FFD700", "name": "yellow"},
        "love": {"code": "#FF69B4", "name": "pink"},  # Hot Pink
        "excitement": {"code": "#FF6347", "name": "orange"},  # Tomato
        "calm": {"code": "#87CEEB", "name": "blue"},  # Sky Blue
        "sadness": {"code": "#4169E1", "name": "blue"},  # Royal Blue
        "anger": {"code": "#DC143C", "name": "red"},  # Crimson
        "fear": {"code": "#9370DB", "name": "purple"},  # Medium Purple
        "anxiety": {"code": "#8B008B", "name": "purple"},  # Dark Magenta
        "disgust": {"code": "#556B2F", "name": "green"},  # Dark Olive Green
        "surprise": {"code": "#FF8C00", "name": "orange"},  # Dark Orange
        "neutral": {"code": "#D3D3D3", "name": "purple"},  # Light Gray -> purple for default
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
        """Compute aura color from emotion distribution."""
        # Get color for dominant emotion
        color_info = self.EMOTION_COLORS.get(dominant.lower(), {"code": "#D3D3D3", "name": "purple"})
        
        # For now, return base color
        # Could implement color blending for mixed emotions
        return color_info
    
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
        aura_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "date": target_date.isoformat(),
            "color": "purple",
            "color_code": "#D3D3D3",
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
