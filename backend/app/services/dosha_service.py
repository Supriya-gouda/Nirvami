"""Dosha assessment service."""
from typing import Dict
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DoshaService:
    """Service for dosha assessment and Ayurvedic recommendations."""
    
    # Dosha assessment logic based on quiz responses
    VATA_INDICATORS = ["thin", "dry_skin", "anxious", "creative", "cold", "irregular"]
    PITTA_INDICATORS = ["medium_build", "warm", "competitive", "focused", "irritable", "oily_skin"]
    KAPHA_INDICATORS = ["heavy_build", "calm", "steady", "slow", "cool", "thick_skin"]
    
    async def assess_dosha(
        self,
        user_id: str,
        quiz_responses: Dict,
        supabase
    ) -> Dict:
        """
        Assess dosha type from quiz responses.
        
        Args:
            user_id: User ID
            quiz_responses: Dictionary of quiz answers
            supabase: Supabase client
            
        Returns:
            Dosha assessment data
        """
        try:
            # Calculate dosha scores
            vata_score = self._calculate_vata_score(quiz_responses)
            pitta_score = self._calculate_pitta_score(quiz_responses)
            kapha_score = self._calculate_kapha_score(quiz_responses)
            
            # Determine primary and secondary doshas
            scores = {
                "vata": vata_score,
                "pitta": pitta_score,
                "kapha": kapha_score
            }
            sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            primary_dosha = sorted_doshas[0][0]
            secondary_dosha = sorted_doshas[1][0] if sorted_doshas[1][1] > 30 else None
            
            # Create assessment record
            assessment_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "assessment_date": datetime.now().isoformat(),
                "quiz_responses": quiz_responses,
                "vata_score": vata_score,
                "pitta_score": pitta_score,
                "kapha_score": kapha_score,
                "primary_dosha": primary_dosha,
                "secondary_dosha": secondary_dosha,
                "assessment_type": "full"
            }
            
            # Save assessment
            result = supabase.table("dosha_assessments").insert(assessment_data).execute()
            
            # Update user profile with dosha type
            dosha_type = f"{primary_dosha}-{secondary_dosha}" if secondary_dosha else primary_dosha
            supabase.table("profiles").update({
                "dosha_type": dosha_type
            }).eq("id", user_id).execute()
            
            return result.data[0] if result.data else assessment_data
            
        except Exception as e:
            logger.error(f"Error assessing dosha: {e}")
            raise
    
    def _calculate_vata_score(self, responses: Dict) -> float:
        """Calculate Vata score from responses."""
        score = 0
        total = 0
        
        for key, value in responses.items():
            if any(indicator in str(value).lower() for indicator in self.VATA_INDICATORS):
                score += 1
            total += 1
        
        return (score / total * 100) if total > 0 else 33.33
    
    def _calculate_pitta_score(self, responses: Dict) -> float:
        """Calculate Pitta score from responses."""
        score = 0
        total = 0
        
        for key, value in responses.items():
            if any(indicator in str(value).lower() for indicator in self.PITTA_INDICATORS):
                score += 1
            total += 1
        
        return (score / total * 100) if total > 0 else 33.33
    
    def _calculate_kapha_score(self, responses: Dict) -> float:
        """Calculate Kapha score from responses."""
        score = 0
        total = 0
        
        for key, value in responses.items():
            if any(indicator in str(value).lower() for indicator in self.KAPHA_INDICATORS):
                score += 1
            total += 1
        
        return (score / total * 100) if total > 0 else 33.33
    
    async def get_recommendations(self, user_id: str, supabase) -> Dict:
        """Get personalized Ayurvedic recommendations."""
        try:
            # Get user's dosha type
            profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
            dosha_type = profile.data.get("dosha_type") if profile.data else "vata"
            
            # Get relevant resources
            resources = supabase.table("ayurveda_resources").select("*").contains(
                "dosha_tags", [dosha_type.split("-")[0]]
            ).limit(10).execute()
            
            # Build recommendations
            recommendations = {
                "dosha_type": dosha_type,
                "diet": self._get_diet_recommendations(dosha_type),
                "lifestyle": self._get_lifestyle_recommendations(dosha_type),
                "yoga": self._get_yoga_recommendations(dosha_type),
                "resources": resources.data if resources.data else []
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise
    
    def _get_diet_recommendations(self, dosha_type: str) -> list:
        """Get diet recommendations for dosha type."""
        primary = dosha_type.split("-")[0]
        
        recommendations = {
            "vata": [
                "Favor warm, cooked foods",
                "Include healthy fats like ghee and sesame oil",
                "Eat sweet fruits like bananas and avocados",
                "Avoid cold, raw, and dry foods"
            ],
            "pitta": [
                "Choose cooling foods like cucumber and coconut",
                "Favor sweet, bitter, and astringent tastes",
                "Avoid spicy, salty, and sour foods",
                "Include mint, cilantro, and fennel"
            ],
            "kapha": [
                "Eat light, warm, and dry foods",
                "Include spices like ginger, black pepper, and turmeric",
                "Favor bitter and astringent vegetables",
                "Reduce heavy, oily, and sweet foods"
            ]
        }
        
        return recommendations.get(primary, recommendations["vata"])
    
    def _get_lifestyle_recommendations(self, dosha_type: str) -> list:
        """Get lifestyle recommendations."""
        primary = dosha_type.split("-")[0]
        
        recommendations = {
            "vata": [
                "Maintain a regular daily routine",
                "Practice grounding activities like meditation",
                "Get adequate rest and sleep",
                "Stay warm and avoid cold, windy conditions"
            ],
            "pitta": [
                "Practice cooling pranayama",
                "Avoid excessive heat and sun exposure",
                "Engage in moderate exercise",
                "Cultivate patience and relaxation"
            ],
            "kapha": [
                "Stay active with regular exercise",
                "Wake up early and avoid daytime naps",
                "Seek variety and stimulation",
                "Practice energizing breathwork"
            ]
        }
        
        return recommendations.get(primary, recommendations["vata"])
    
    def _get_yoga_recommendations(self, dosha_type: str) -> list:
        """Get yoga recommendations."""
        primary = dosha_type.split("-")[0]
        
        recommendations = {
            "vata": [
                "Grounding poses like Mountain Pose and Tree Pose",
                "Slow, gentle flows",
                "Forward bends for calming",
                "Restorative yoga"
            ],
            "pitta": [
                "Cooling poses like forward folds",
                "Avoid intense inversions",
                "Practice with mindfulness and ease",
                "Include twists for detoxification"
            ],
            "kapha": [
                "Energizing poses like Sun Salutations",
                "Backbends for opening",
                "Dynamic, flowing sequences",
                "Challenging balances"
            ]
        }
        
        return recommendations.get(primary, recommendations["vata"])
