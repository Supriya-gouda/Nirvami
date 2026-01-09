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
        10: "vata",  # decision making
        11: "pitta", # speech
        12: "kapha"  # walking pace
    }
    
    @staticmethod
    def calculate_scores(answers: List[DoshaAnswer]) -> dict:
        """
        Calculate dosha percentages using simple counting method.
        
        Each answer maps to exactly one dosha and contributes 1 point.
        Percentages calculated as (count / total) * 100.
        
        Args:
            answers: List of DoshaAnswer objects with selected_dosha field
            
        Returns:
            Dictionary with percentages, primary/secondary doshas, and result_type
        """
        # Initialize counters
        vata_count = 0
        pitta_count = 0
        kapha_count = 0
        
        # Count selections - each answer contributes exactly 1 point
        for answer in answers:
            selected_dosha = answer.selected_dosha.lower()
            if selected_dosha == "vata":
                vata_count += 1
            elif selected_dosha == "pitta":
                pitta_count += 1
            elif selected_dosha == "kapha":
                kapha_count += 1
        
        # Calculate total (should equal number of questions)
        total = vata_count + pitta_count + kapha_count
        if total == 0:
            total = 1  # Avoid division by zero
            
        # Calculate percentages
        vata_percent = round((vata_count / total) * 100, 2)
        pitta_percent = round((pitta_count / total) * 100, 2)
        kapha_percent = round((kapha_count / total) * 100, 2)

        # Create sorted list of doshas by percentage (descending)
        dosha_percentages = [
            ("vata", vata_percent),
            ("pitta", pitta_percent),
            ("kapha", kapha_percent)
        ]
        dosha_percentages.sort(key=lambda x: x[1], reverse=True)
        
        # Determine primary dosha (highest percentage)
        primary_dosha = dosha_percentages[0][0]
        secondary_dosha = None
        result_type = "single"
        
        # Check for Tri-Dosha (all within 10% range)
        max_percent = dosha_percentages[0][1]
        min_percent = dosha_percentages[2][1]
        if max_percent - min_percent <= 10:
            result_type = "tri"
            secondary_dosha = None  # Tri-doshic has no secondary
        else:
            # Check for Dual Dosha (top 2 within 10% difference)
            top1_percent = dosha_percentages[0][1]
            top2_percent = dosha_percentages[1][1]
            if top1_percent - top2_percent <= 10:
                result_type = "dual"
                secondary_dosha = dosha_percentages[1][0]
        
        return {
            "vata_count": vata_count,
            "pitta_count": pitta_count,
            "kapha_count": kapha_count,
            "vata_percent": vata_percent,
            "pitta_percent": pitta_percent,
            "kapha_percent": kapha_percent,
            "primary_dosha": primary_dosha,
            "secondary_dosha": secondary_dosha,
            "result_type": result_type,
            "dominant_dosha": primary_dosha  # For backward compatibility
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
