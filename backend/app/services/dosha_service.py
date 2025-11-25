"""Dosha assessment service."""
from typing import Dict, List
import uuid
from datetime import datetime
import logging
from app.models.schemas import DoshaAnswer

logger = logging.getLogger(__name__)


class DoshaService:
    """Service for dosha assessment and Ayurvedic recommendations."""
    
    # Question ID to Dosha mapping based on frontend quiz structure
    # Questions 1, 4, 7, 10 are Vata-focused
    # Questions 2, 5, 8 are Pitta-focused  
    # Questions 3, 6, 9 are Kapha-focused
    QUESTION_DOSHA_MAP = {
        1: "vata",   # body frame
        2: "pitta",  # skin type
        3: "kapha",  # appetite
        4: "vata",   # stress handling
        5: "pitta",  # sleep pattern
        6: "kapha",  # energy levels
        7: "vata",   # body temperature
        8: "pitta",  # learning style
        9: "kapha",  # digestion
        10: "vata"   # decision making
    }
    
    @staticmethod
    def calculate_scores(answers: List[DoshaAnswer]) -> dict:
        """
        Calculate dosha scores from quiz answers.
        
        Args:
            answers: List of DoshaAnswer objects with question_id and answer_value
            
        Returns:
            Dictionary with vata_score, pitta_score, kapha_score, dominant_dosha
        """
        vata_score = 0
        pitta_score = 0
        kapha_score = 0
        
        # Sum up scores based on question-to-dosha mapping
        for answer in answers:
            question_id = answer.question_id
            score_value = answer.answer_value
            
            # Map question to dosha category
            dosha_category = DoshaService.QUESTION_DOSHA_MAP.get(question_id)
            
            if dosha_category == "vata":
                vata_score += score_value
            elif dosha_category == "pitta":
                pitta_score += score_value
            elif dosha_category == "kapha":
                kapha_score += score_value
        
        # Determine dominant dosha
        scores = {
            "vata": vata_score,
            "pitta": pitta_score,
            "kapha": kapha_score
        }
        dominant_dosha = max(scores, key=scores.get)
        
        # Determine secondary dosha (if score is within 20% of dominant)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        secondary_dosha = None
        if len(sorted_scores) > 1:
            threshold = sorted_scores[0][1] * 0.8
            if sorted_scores[1][1] >= threshold:
                secondary_dosha = sorted_scores[1][0]
        
        return {
            "vata_score": vata_score,
            "pitta_score": pitta_score,
            "kapha_score": kapha_score,
            "dominant_dosha": dominant_dosha,
            "primary_dosha": dominant_dosha,
            "secondary_dosha": secondary_dosha
        }
    
    # Legacy indicators for backward compatibility
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
    
    @staticmethod
    def get_diet_recommendations(dosha_type: str, supabase) -> list:
        """Get diet recommendations from database."""
        primary = dosha_type.split("-")[0].lower()
        
        try:
            result = supabase.table("ayurveda_resources")\
                .select("content")\
                .eq("category", "diet")\
                .contains("dosha_tags", [primary])\
                .execute()
            
            if result.data:
                return [item["content"] for item in result.data]
            return []
        except Exception as e:
            logger.error(f"Error fetching diet recommendations: {e}")
            return []
    
    @staticmethod
    def get_lifestyle_recommendations(dosha_type: str, supabase) -> list:
        """Get lifestyle recommendations from database."""
        primary = dosha_type.split("-")[0].lower()
        
        try:
            result = supabase.table("ayurveda_resources")\
                .select("content")\
                .eq("category", "lifestyle")\
                .contains("dosha_tags", [primary])\
                .execute()
            
            if result.data:
                return [item["content"] for item in result.data]
            return []
        except Exception as e:
            logger.error(f"Error fetching lifestyle recommendations: {e}")
            return []
    
    @staticmethod
    def get_yoga_recommendations(dosha_type: str, supabase) -> list:
        """Get yoga recommendations from database."""
        primary = dosha_type.split("-")[0].lower()
        
        try:
            result = supabase.table("ayurveda_resources")\
                .select("content")\
                .eq("category", "yoga")\
                .contains("dosha_tags", [primary])\
                .execute()
            
            if result.data:
                return [item["content"] for item in result.data]
            return []
        except Exception as e:
            logger.error(f"Error fetching yoga recommendations: {e}")
            return []
