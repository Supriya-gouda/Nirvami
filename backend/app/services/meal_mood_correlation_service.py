"""
Meal-Mood Correlation Service
Handles correlation analysis between meals and emotion logs for personalized insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

from app.utils.database import get_supabase
from app.services.meal_service import MealService

logger = logging.getLogger(__name__)

@dataclass
class MealMoodCorrelation:
    """Data class for meal-mood correlation results"""
    meal_ingredient: str
    meal_type: str
    positive_correlation: float  # -1 to 1
    negative_correlation: float  # -1 to 1
    correlation_strength: str    # weak, moderate, strong
    sample_size: int
    insights: List[str]

class MealMoodCorrelationService:
    """Service for analyzing correlations between meals and mood"""
    
    def __init__(self):
        self.meal_service = MealService()
        
    async def calculate_meal_mood_correlations(
        self, 
        user_id: str, 
        days: int = 30
    ) -> List[MealMoodCorrelation]:
        """
        Calculate correlations between meals and mood changes
        
        Args:
            user_id: User identifier
            days: Number of days to analyze (default 30)
            
        Returns:
            List of meal-mood correlations
        """
        try:
            logger.info(f"Calculating meal-mood correlations for user {user_id} over {days} days")
            
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get meal and emotion data
            meals = await self._get_user_meals(user_id, start_date, end_date)
            emotions = await self._get_user_emotions(user_id, start_date, end_date)
            
            if not meals or not emotions:
                logger.warning(f"Insufficient data for correlation analysis. Meals: {len(meals)}, Emotions: {len(emotions)}")
                return []
            
            # Calculate correlations
            correlations = await self._analyze_correlations(meals, emotions)
            
            # Store correlation results
            await self._store_correlations(user_id, correlations)
            
            logger.info(f"Calculated {len(correlations)} meal-mood correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating meal-mood correlations: {e}")
            raise

    async def get_meal_mood_insights(
        self, 
        user_id: str, 
        meal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get personalized meal-mood insights for a user
        
        Args:
            user_id: User identifier
            meal_type: Optional meal type filter (breakfast, lunch, dinner, snack)
            
        Returns:
            Dictionary with meal-mood insights
        """
        try:
            logger.info(f"Getting meal-mood insights for user {user_id}")
            
            supabase = get_supabase(use_service_role=True)
            
            # Build query
            query = supabase.table('meal_emotion_correlations').select('*').eq('user_id', user_id)
            
            if meal_type:
                query = query.eq('meal_type', meal_type)
            
            # Get correlations
            response = query.order('correlation_score', desc=True).limit(10).execute()
            correlations = response.data
            
            if not correlations:
                return {
                    'insights': ['Not enough data for personalized insights yet. Keep logging meals and emotions!'],
                    'top_positive_foods': [],
                    'foods_to_moderate': [],
                    'recommendations': []
                }
            
            # Process insights
            insights = await self._generate_insights(correlations)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting meal-mood insights: {e}")
            raise

    async def _get_user_meals(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get user meals within date range"""
        try:
            supabase = get_supabase(use_service_role=True)
            
            response = supabase.table('meals').select('*').eq('user_id', user_id)\
                .gte('meal_time', start_date.isoformat())\
                .lte('meal_time', end_date.isoformat())\
                .order('meal_time', desc=False).execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"Error getting user meals: {e}")
            return []

    async def _get_user_emotions(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get user emotions within date range"""
        try:
            supabase = get_supabase(use_service_role=True)
            
            response = supabase.table('emotion_logs').select('*').eq('user_id', user_id)\
                .gte('created_at', start_date.isoformat())\
                .lte('created_at', end_date.isoformat())\
                .order('created_at', desc=False).execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"Error getting user emotions: {e}")
            return []

    async def _analyze_correlations(
        self, 
        meals: List[Dict[str, Any]], 
        emotions: List[Dict[str, Any]]
    ) -> List[MealMoodCorrelation]:
        """Analyze correlations between meals and emotions"""
        correlations = []
        
        try:
            # Group emotions by time windows
            emotion_windows = self._create_emotion_windows(emotions)
            
            # Analyze each meal's impact on subsequent emotions
            for meal in meals:
                meal_time = datetime.fromisoformat(meal['meal_time'].replace('Z', '+00:00'))
                
                # Find emotions 1-6 hours after meal
                post_meal_emotions = self._find_post_meal_emotions(meal_time, emotion_windows)
                
                if not post_meal_emotions:
                    continue
                
                # Extract ingredients from meal
                ingredients = meal.get('extracted_ingredients', [])
                if isinstance(ingredients, str):
                    ingredients = json.loads(ingredients)
                
                # Calculate correlation for each ingredient
                for ingredient in ingredients:
                    correlation = self._calculate_ingredient_emotion_correlation(
                        ingredient, meal, post_meal_emotions
                    )
                    if correlation:
                        correlations.append(correlation)
            
            # Aggregate and rank correlations
            aggregated_correlations = self._aggregate_correlations(correlations)
            
            return aggregated_correlations
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return []

    def _create_emotion_windows(self, emotions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Create time-based windows of emotions"""
        windows = {}
        
        for emotion in emotions:
            emotion_time = datetime.fromisoformat(emotion['created_at'].replace('Z', '+00:00'))
            hour_key = emotion_time.strftime('%Y-%m-%d-%H')
            
            if hour_key not in windows:
                windows[hour_key] = []
            windows[hour_key].append(emotion)
        
        return windows

    def _find_post_meal_emotions(
        self, 
        meal_time: datetime, 
        emotion_windows: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Find emotions occurring 1-6 hours after a meal"""
        post_meal_emotions = []
        
        # Check 6 hours after meal
        for hour_offset in range(1, 7):
            check_time = meal_time + timedelta(hours=hour_offset)
            hour_key = check_time.strftime('%Y-%m-%d-%H')
            
            if hour_key in emotion_windows:
                post_meal_emotions.extend(emotion_windows[hour_key])
        
        return post_meal_emotions

    def _calculate_ingredient_emotion_correlation(
        self, 
        ingredient: str, 
        meal: Dict[str, Any], 
        emotions: List[Dict[str, Any]]
    ) -> Optional[MealMoodCorrelation]:
        """Calculate correlation between an ingredient and emotions"""
        if not emotions:
            return None
        
        # Map emotions to sentiment scores
        emotion_scores = []
        for emotion in emotions:
            score = self._emotion_to_score(emotion['primary_emotion'])
            emotion_scores.append(score)
        
        # Calculate average emotional impact
        avg_score = sum(emotion_scores) / len(emotion_scores)
        
        # Determine correlation strength
        correlation_strength = 'weak'
        if abs(avg_score) > 0.3:
            correlation_strength = 'moderate'
        if abs(avg_score) > 0.6:
            correlation_strength = 'strong'
        
        # Generate insights
        insights = self._generate_ingredient_insights(ingredient, avg_score, len(emotions))
        
        return MealMoodCorrelation(
            meal_ingredient=ingredient,
            meal_type=meal['meal_type'],
            positive_correlation=max(0, avg_score),
            negative_correlation=abs(min(0, avg_score)),
            correlation_strength=correlation_strength,
            sample_size=len(emotions),
            insights=insights
        )

    def _emotion_to_score(self, emotion: str) -> float:
        """Convert emotion to numerical score (-1 to 1)"""
        positive_emotions = {
            'joy': 0.8, 'happiness': 0.8, 'contentment': 0.6, 'calm': 0.5,
            'excited': 0.7, 'grateful': 0.6, 'peaceful': 0.5, 'confident': 0.6
        }
        
        negative_emotions = {
            'sadness': -0.6, 'anger': -0.8, 'frustrated': -0.7, 'anxious': -0.7,
            'stressed': -0.6, 'overwhelmed': -0.8, 'disappointed': -0.5, 'worried': -0.6
        }
        
        emotion_lower = emotion.lower()
        
        if emotion_lower in positive_emotions:
            return positive_emotions[emotion_lower]
        elif emotion_lower in negative_emotions:
            return negative_emotions[emotion_lower]
        else:
            return 0.0  # Neutral

    def _generate_ingredient_insights(
        self, 
        ingredient: str, 
        avg_score: float, 
        sample_size: int
    ) -> List[str]:
        """Generate insights for ingredient-emotion correlation"""
        insights = []
        
        if avg_score > 0.3:
            insights.append(f"{ingredient.title()} seems to have a positive effect on your mood")
            if avg_score > 0.6:
                insights.append(f"Consider including {ingredient} more often for mood support")
        elif avg_score < -0.3:
            insights.append(f"{ingredient.title()} may be affecting your mood negatively")
            if avg_score < -0.6:
                insights.append(f"Consider reducing {ingredient} intake or trying alternatives")
        
        if sample_size < 5:
            insights.append("More data needed for reliable correlation")
        
        return insights

    def _aggregate_correlations(
        self, 
        correlations: List[MealMoodCorrelation]
    ) -> List[MealMoodCorrelation]:
        """Aggregate correlations by ingredient"""
        ingredient_data = {}
        
        for correlation in correlations:
            ingredient = correlation.meal_ingredient
            
            if ingredient not in ingredient_data:
                ingredient_data[ingredient] = {
                    'positive_scores': [],
                    'negative_scores': [],
                    'meal_types': [],
                    'total_samples': 0,
                    'insights': set()
                }
            
            data = ingredient_data[ingredient]
            data['positive_scores'].append(correlation.positive_correlation)
            data['negative_scores'].append(correlation.negative_correlation)
            data['meal_types'].append(correlation.meal_type)
            data['total_samples'] += correlation.sample_size
            data['insights'].update(correlation.insights)
        
        # Create aggregated correlations
        aggregated = []
        for ingredient, data in ingredient_data.items():
            avg_positive = sum(data['positive_scores']) / len(data['positive_scores'])
            avg_negative = sum(data['negative_scores']) / len(data['negative_scores'])
            
            # Determine overall correlation strength
            overall_strength = 'weak'
            max_correlation = max(avg_positive, avg_negative)
            if max_correlation > 0.3:
                overall_strength = 'moderate'
            if max_correlation > 0.6:
                overall_strength = 'strong'
            
            aggregated.append(MealMoodCorrelation(
                meal_ingredient=ingredient,
                meal_type=max(set(data['meal_types']), key=data['meal_types'].count),
                positive_correlation=avg_positive,
                negative_correlation=avg_negative,
                correlation_strength=overall_strength,
                sample_size=data['total_samples'],
                insights=list(data['insights'])
            ))
        
        # Sort by correlation strength
        return sorted(aggregated, key=lambda x: max(x.positive_correlation, x.negative_correlation), reverse=True)

    async def _store_correlations(
        self, 
        user_id: str, 
        correlations: List[MealMoodCorrelation]
    ) -> None:
        """Store correlation results in database"""
        try:
            supabase = get_supabase(use_service_role=True)
            
            # Clear existing correlations for user
            supabase.table('meal_emotion_correlations').delete().eq('user_id', user_id).execute()
            
            # Insert new correlations
            correlation_data = []
            for correlation in correlations:
                correlation_data.append({
                    'user_id': user_id,
                    'ingredient_name': correlation.meal_ingredient,
                    'meal_type': correlation.meal_type,
                    'correlation_score': max(correlation.positive_correlation, correlation.negative_correlation),
                    'correlation_type': 'positive' if correlation.positive_correlation > correlation.negative_correlation else 'negative',
                    'confidence_level': correlation.correlation_strength,
                    'sample_size': correlation.sample_size,
                    'insights': json.dumps(correlation.insights),
                    'analyzed_at': datetime.now().isoformat()
                })
            
            if correlation_data:
                supabase.table('meal_emotion_correlations').insert(correlation_data).execute()
                logger.info(f"Stored {len(correlation_data)} correlations for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing correlations: {e}")

    async def _generate_insights(self, correlations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive meal-mood insights"""
        try:
            # Separate positive and negative correlations
            positive_foods = [c for c in correlations if c['correlation_type'] == 'positive']
            negative_foods = [c for c in correlations if c['correlation_type'] == 'negative']
            
            # Sort by correlation score
            positive_foods.sort(key=lambda x: x['correlation_score'], reverse=True)
            negative_foods.sort(key=lambda x: x['correlation_score'], reverse=True)
            
            # Generate insights
            insights = []
            
            if positive_foods:
                top_positive = positive_foods[:3]
                insight = f"Foods that boost your mood: {', '.join([f['ingredient_name'] for f in top_positive])}"
                insights.append(insight)
            
            if negative_foods:
                top_negative = negative_foods[:3]
                insight = f"Foods that may affect your mood: {', '.join([f['ingredient_name'] for f in top_negative])}"
                insights.append(insight)
            
            # Meal type insights
            meal_type_analysis = self._analyze_meal_type_patterns(correlations)
            insights.extend(meal_type_analysis)
            
            return {
                'insights': insights,
                'top_positive_foods': positive_foods[:5],
                'foods_to_moderate': negative_foods[:5],
                'recommendations': self._generate_recommendations(positive_foods, negative_foods)
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {'insights': [], 'top_positive_foods': [], 'foods_to_moderate': [], 'recommendations': []}

    def _analyze_meal_type_patterns(self, correlations: List[Dict[str, Any]]) -> List[str]:
        """Analyze patterns by meal type"""
        meal_type_scores = {}
        
        for correlation in correlations:
            meal_type = correlation['meal_type']
            score = correlation['correlation_score']
            
            if correlation['correlation_type'] == 'negative':
                score = -score
            
            if meal_type not in meal_type_scores:
                meal_type_scores[meal_type] = []
            meal_type_scores[meal_type].append(score)
        
        insights = []
        for meal_type, scores in meal_type_scores.items():
            avg_score = sum(scores) / len(scores)
            
            if avg_score > 0.3:
                insights.append(f"Your {meal_type} choices generally support positive mood")
            elif avg_score < -0.3:
                insights.append(f"Consider reviewing your {meal_type} choices for better mood support")
        
        return insights

    def _generate_recommendations(
        self, 
        positive_foods: List[Dict[str, Any]], 
        negative_foods: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if positive_foods:
            top_positive = positive_foods[0]['ingredient_name']
            recommendations.append(f"Try incorporating more {top_positive} into your meals")
        
        if negative_foods:
            top_negative = negative_foods[0]['ingredient_name']
            recommendations.append(f"Consider moderating {top_negative} intake or trying alternatives")
        
        recommendations.append("Keep logging both meals and emotions for more personalized insights")
        recommendations.append("Try eating mood-boosting foods during stressful periods")
        
        return recommendations