"""Aura computation service."""
from datetime import date, datetime
from typing import Dict
import uuid
import logging

logger = logging.getLogger(__name__)


class AuraService:
    """Service for generating and managing aura visualizations."""
    
    # Comprehensive Aura Mapping based on mood/emotional state
    AURA_MAPPINGS = {
        "balanced_calm": {
            "name": "Balanced & Calm",
            "color_code": "green-blue",
            "gradient": ["#66BB6A", "#42A5F5", "#26A69A"],
            "why": "Green and blue represent emotional balance, healing, and serenity. They appear when the nervous system is regulated and the mind is stable.",
            "what_it_does": "Reduces internal tension, encourages compassion and harmony, supports steady breathing and calmness",
            "purpose": "Restore emotional equilibrium, promote peaceful grounded energy, strengthen resilience",
            "chakra": "Heart + Throat",
            "element": "Air",
            "triggers": ["calm", "peace", "relaxed", "balanced", "serene"]
        },
        "energized_active": {
            "name": "Energized & Active",
            "color_code": "yellow",
            "gradient": ["#FDD835", "#FFEB3B", "#FBC02D"],
            "why": "Yellow represents vitality, alertness, and internal fire. It appears when motivation and physical energy are high.",
            "what_it_does": "Boosts enthusiasm, enhances confidence & optimism, activates personal power",
            "purpose": "Support active movement, encourage productivity & engagement, strengthen creative flow",
            "chakra": "Solar Plexus",
            "element": "Fire",
            "triggers": ["energetic", "active", "motivated", "enthusiastic", "alert"]
        },
        "stressed_anxious": {
            "name": "Stressed & Anxious",
            "color_code": "red",
            "gradient": ["#E53935", "#D32F2F", "#C62828"],
            "why": "Red signifies overstimulation of the root chakra — fight-or-flight activation.",
            "what_it_does": "Exposes emotional overload, reveals inner turbulence, highlights the need for grounding",
            "purpose": "Warn the user of high stress, encourage grounding practices, bring awareness to emotional imbalance",
            "chakra": "Root",
            "element": "Fire + Air imbalance",
            "triggers": ["stress", "anxiety", "anxious", "worried", "tense", "nervous"]
        },
        "focused_sharp": {
            "name": "Focused & Sharp",
            "color_code": "indigo",
            "gradient": ["#3F51B5", "#303F9F", "#1A237E"],
            "why": "Indigo activates the third eye, representing insight, clarity, and deep mental focus.",
            "what_it_does": "Enhances problem-solving, increases perception, deepens intuition",
            "purpose": "Support concentration, align intellect with wisdom, strengthen clarity of thought",
            "chakra": "Third Eye",
            "element": "Ether",
            "triggers": ["focused", "concentrated", "sharp", "clear-minded", "attentive"]
        },
        "tired_drained": {
            "name": "Tired & Drained",
            "color_code": "blue-grey",
            "gradient": ["#90A4AE", "#78909C", "#546E7A"],
            "why": "Blue-grey symbolizes low vitality, fatigue, and energy depletion.",
            "what_it_does": "Indicates the need for rest, slows mental pacing, encourages recovery",
            "purpose": "Promote recuperation, reduce mental strain, guide user toward self-care",
            "chakra": "Throat",
            "element": "Water",
            "triggers": ["tired", "exhausted", "drained", "fatigued", "weary", "low-energy"]
        },
        "joyful_happy": {
            "name": "Joyful & Happy",
            "color_code": "yellow",
            "gradient": ["#FFEB3B", "#FDD835", "#FBC02D"],
            "why": "Yellow radiates positivity, lightness, and emotional warmth.",
            "what_it_does": "Lifts mood, enhances creativity, expands emotional openness",
            "purpose": "Encourage engagement, support social connection, reinforce emotional wellness",
            "chakra": "Solar Plexus",
            "element": "Fire",
            "triggers": ["joy", "happy", "happiness", "cheerful", "delighted", "pleased"]
        },
        "sad_low": {
            "name": "Sad & Low",
            "color_code": "deep-blue",
            "gradient": ["#1976D2", "#1565C0", "#0D47A1"],
            "why": "Deep blue reflects emotional heaviness, introspection, and longing.",
            "what_it_does": "Encourages emotional release, promotes reflection & healing, slows emotional turbulence",
            "purpose": "Support grief processing, bring emotional comfort, create safe emotional space",
            "chakra": "Throat + Crown",
            "element": "Water",
            "triggers": ["sadness", "sad", "down", "low", "melancholy", "gloomy", "blue"]
        },
        "angry_frustrated": {
            "name": "Angry & Frustrated",
            "color_code": "intense-red",
            "gradient": ["#D32F2F", "#C62828", "#B71C1C"],
            "why": "Red appears during emotional overheating — anger, pressure, irritation.",
            "what_it_does": "Alerts user of emotional overload, reveals internal conflict, increases self-awareness of triggers",
            "purpose": "Encourage cooling/grounding practices, prevent emotional outburst, reduce internal tension",
            "chakra": "Root",
            "element": "Fire",
            "triggers": ["anger", "angry", "frustrated", "irritated", "furious", "mad", "rage"]
        },
        "peaceful_content": {
            "name": "Peaceful & Content",
            "color_code": "white",
            "gradient": ["#FFFFFF", "#F5F5F5", "#EEEEEE"],
            "why": "White symbolizes clarity, harmony, and completion — unity of all colors.",
            "what_it_does": "Brings emotional stillness, supports acceptance, enhances spiritual balance",
            "purpose": "Reinforce positivity, support restful mental states, maintain inner alignment",
            "chakra": "Crown",
            "element": "Ether",
            "triggers": ["peaceful", "content", "satisfied", "harmonious", "tranquil"]
        },
        "confused_uncertain": {
            "name": "Confused & Uncertain",
            "color_code": "grey-yellow",
            "gradient": ["#9E9E9E", "#BDBDBD", "#E0E0E0"],
            "why": "Grey symbolizes fog or lack of direction; pale yellow represents searching for clarity.",
            "what_it_does": "Exposes mental instability, encourages grounding, highlights need for clarity",
            "purpose": "Guide user to structured thinking, reduce uncertainty, promote mindful decision-making",
            "chakra": "Solar Plexus",
            "element": "Air",
            "triggers": ["confused", "uncertain", "doubtful", "unsure", "puzzled", "perplexed"]
        },
        "motivated_driven": {
            "name": "Motivated & Driven",
            "color_code": "gold",
            "gradient": ["#FFD700", "#FFC107", "#FFB300"],
            "why": "Gold denotes ambition, purpose, and transformational energy.",
            "what_it_does": "Boosts confidence, reinforces goal-oriented mindset, activates personal power",
            "purpose": "Support progress, encourage disciplined action, strengthen inner strength",
            "chakra": "Solar Plexus",
            "element": "Fire",
            "triggers": ["motivated", "driven", "determined", "ambitious", "purposeful"]
        },
        "overwhelmed": {
            "name": "Overwhelmed",
            "color_code": "dark-grey",
            "gradient": ["#616161", "#424242", "#212121"],
            "why": "Dark grey represents emotional overload and system saturation.",
            "what_it_does": "Signals cognitive burden, indicates emotional exhaustion, draws attention to stressors",
            "purpose": "Encourage step-back and rest, prevent burnout, re-establish emotional boundaries",
            "chakra": "Root",
            "element": "Earth",
            "triggers": ["overwhelmed", "overloaded", "stressed-out", "swamped", "burdened"]
        },
        "creative_inspired": {
            "name": "Creative & Inspired",
            "color_code": "orange",
            "gradient": ["#FF9800", "#FB8C00", "#F57C00"],
            "why": "Orange is the color of the sacral chakra — creativity, expression, imagination.",
            "what_it_does": "Stimulates inspiration, encourages expressive thinking, enhances artistic flow",
            "purpose": "Support creative output, improve ideation, strengthen expressive confidence",
            "chakra": "Sacral",
            "element": "Water + Fire",
            "triggers": ["creative", "inspired", "imaginative", "artistic", "inventive"]
        },
        "restless_agitated": {
            "name": "Restless & Agitated",
            "color_code": "orange-red",
            "gradient": ["#FF5722", "#F4511E", "#E64A19"],
            "why": "Orange-red indicates hyperactive energy and internal agitation.",
            "what_it_does": "Reveals disrupted emotional balance, increases awareness of impulsivity, highlights nervous restlessness",
            "purpose": "Encourage grounding, reduce scattered energy, support calm breathing practices",
            "chakra": "Root + Sacral",
            "element": "Fire + Air",
            "triggers": ["restless", "agitated", "fidgety", "uneasy", "jumpy", "hyperactive"]
        },
        "grateful_thankful": {
            "name": "Grateful & Thankful",
            "color_code": "pink",
            "gradient": ["#EC407A", "#E91E63", "#D81B60"],
            "why": "Pink symbolizes compassion, emotional warmth, and heart expansion.",
            "what_it_does": "Encourages kindness, promotes self-love, strengthens emotional bonding",
            "purpose": "Enhance empathy, support loving relationships, promote positivity and gratitude",
            "chakra": "Heart",
            "element": "Air",
            "triggers": ["grateful", "thankful", "appreciative", "blessed", "gratitude"]
        },
        "neutral": {
            "name": "Neutral State",
            "color_code": "grey",
            "gradient": ["#9E9E9E", "#BDBDBD", "#E0E0E0"],
            "why": "Grey represents neutrality, pause, or absence of emotional signal.",
            "what_it_does": "Creates emotional reset, avoids false interpretation, encourages user to interact/log mood",
            "purpose": "Hold neutral space, indicate the need for fresh emotional input, provide visual baseline",
            "chakra": "All (balanced)",
            "element": "Earth",
            "triggers": ["neutral", "okay", "fine", "average", "normal"]
        }
    }
    
    # Map basic emotions to aura states
    EMOTION_TO_AURA = {
        # Calm states
        "calm": "balanced_calm",
        "peace": "balanced_calm",
        "relaxed": "balanced_calm",
        "balanced": "balanced_calm",
        "serene": "balanced_calm",
        
        # Happy/Joyful states
        "joy": "joyful_happy",
        "happy": "joyful_happy",
        "happiness": "joyful_happy",
        "cheerful": "joyful_happy",
        "delighted": "joyful_happy",
        
        # Sad states
        "sadness": "sad_low",
        "sad": "sad_low",
        "down": "sad_low",
        "low": "sad_low",
        "melancholy": "sad_low",
        
        # Angry/Frustrated states
        "anger": "angry_frustrated",
        "angry": "angry_frustrated",
        "frustrated": "angry_frustrated",
        "irritated": "angry_frustrated",
        
        # Anxious/Stressed states
        "fear": "stressed_anxious",
        "anxiety": "stressed_anxious",
        "anxious": "stressed_anxious",
        "worried": "stressed_anxious",
        "stress": "stressed_anxious",
        
        # Tired/Low energy states
        "tired": "tired_drained",
        "exhausted": "tired_drained",
        "drained": "tired_drained",
        "fatigued": "tired_drained",
        "weary": "tired_drained",
        "low-energy": "tired_drained",
        
        # Energized states
        "energized": "energized_active",
        "energetic": "energized_active",
        "active": "energized_active",
        "motivated": "energized_active",
        
        # Grateful states
        "grateful": "grateful_thankful",
        "thankful": "grateful_thankful",
        "appreciative": "grateful_thankful",
        
        # Confused states
        "confused": "confused_uncertain",
        "uncertain": "confused_uncertain",
        "doubtful": "confused_uncertain",
        
        # Neutral
        "neutral": "neutral"
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
