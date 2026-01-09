"""
Meal Service - Handles meal logging, Ayurvedic analysis, and meal-based recommendations
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4, UUID
import json
import re

from app.utils.database import get_supabase
from app.services.gemini_chatbot import get_chatbot
# from app.ml.model_manager import ModelManager  # Temporarily commented out

logger = logging.getLogger(__name__)

class MealService:
    """Service for meal logging and Ayurvedic meal analysis"""
    
    def __init__(self):
        self.supabase = get_supabase(use_service_role=True)
        self.gemini = get_chatbot()
        # self.model_manager = ModelManager()  # Temporarily disabled for testing
        self.model_manager = None
        
        # Ayurvedic food classification
        self.vata_pacifying = [
            'warm soups', 'cooked grains', 'sweet fruits', 'nuts', 'oils', 
            'dairy', 'rice', 'oats', 'ghee', 'ginger', 'cinnamon', 'dates'
        ]
        self.pitta_pacifying = [
            'cooling foods', 'sweet fruits', 'coconut', 'cucumber', 'leafy greens',
            'sweet vegetables', 'milk', 'ghee', 'cilantro', 'mint', 'fennel'
        ]
        self.kapha_pacifying = [
            'spices', 'light foods', 'bitter vegetables', 'leafy greens',
            'beans', 'lentils', 'ginger', 'turmeric', 'black pepper'
        ]
        
        self.vata_aggravating = ['cold foods', 'raw vegetables', 'dry foods', 'caffeine']
        self.pitta_aggravating = ['spicy food', 'fried items', 'citrus fruits', 'alcohol']
        self.kapha_aggravating = ['heavy foods', 'dairy products', 'sweet foods', 'oily items']

    async def log_meal(self, user_id: str, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log a meal and perform Ayurvedic analysis"""
        try:
            logger.info(f"Logging meal for user {user_id}: {meal_data.get('meal_text', '')}")
            
            # Parse meal data
            meal_text = meal_data.get('meal_text', '').strip()
            meal_type = meal_data.get('meal_type', 'snack').lower()
            meal_time_str = meal_data.get('meal_time')
            notes = meal_data.get('notes', '')
            
            # Parse meal time
            if meal_time_str:
                meal_time = datetime.fromisoformat(meal_time_str.replace('Z', '+00:00'))
            else:
                meal_time = datetime.now()
            
            # Extract ingredients and analyze with AI
            ingredients = await self._extract_ingredients(meal_text)
            dosha_impact = await self._analyze_dosha_impact(meal_text, ingredients)
            
            # Generate embedding for meal content
            embedding = None
            try:
                if self.model_manager:
                    embedding_vector = self.model_manager.get_embedding(meal_text)
                    if embedding_vector is not None:
                        embedding = embedding_vector.tolist()
            except Exception as e:
                logger.warning(f"Failed to generate embedding for meal: {e}")
            
            # Estimate calories (simple estimation)
            estimated_calories = self._estimate_calories(meal_text, ingredients)
            
            # Insert meal into database
            meal_record = {
                'id': str(uuid4()),
                'user_id': user_id,
                'meal_time': meal_time.isoformat(),
                'meal_type': meal_type,
                'meal_text': meal_text,
                'ingredients': ingredients,
                'dosha_impact_tags': dosha_impact,
                'calories': estimated_calories,
                'embedding': embedding,
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('meals').insert(meal_record).execute()
            
            if not result.data:
                raise Exception("Failed to insert meal record")
            
            saved_meal = result.data[0]
            
            # Perform comprehensive Gemini analysis
            analysis_result = await self._perform_comprehensive_meal_analysis(
                user_id, 
                saved_meal['id'],
                meal_text,
                ingredients,
                dosha_impact
            )
            
            # Generate Ayurvedic guidelines for today
            await self._generate_daily_guidelines(user_id, saved_meal['id'])
            
            # Generate recipe suggestions
            await self._generate_recipe_suggestions(user_id)
            
            # Create mood-meal correlation
            await self._create_mood_meal_correlation(user_id, saved_meal['id'])
            
            logger.info(f"Successfully logged meal {saved_meal['id']} for user {user_id}")
            
            # Return meal with analysis
            return {
                **saved_meal,
                'analysis': analysis_result
            }
            
        except Exception as e:
            logger.error(f"Error logging meal for user {user_id}: {e}")
            raise

    async def get_today_meals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all meals for today for a user"""
        try:
            today = date.today()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            
            result = self.supabase.table('meals')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('meal_time', start_of_day.isoformat())\
                .lte('meal_time', end_of_day.isoformat())\
                .order('meal_time')\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting today's meals for user {user_id}: {e}")
            return []

    async def get_weekly_meal_pattern(self, user_id: str) -> Dict[str, Any]:
        """Get weekly meal pattern data for charts"""
        try:
            # Get last 7 days
            end_date = date.today()
            start_date = end_date - timedelta(days=6)
            
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            result = self.supabase.table('meals')\
                .select('meal_time, meal_type')\
                .eq('user_id', user_id)\
                .gte('meal_time', start_datetime.isoformat())\
                .lte('meal_time', end_datetime.isoformat())\
                .execute()
            
            meals = result.data or []
            
            # Process data for weekly pattern
            daily_counts = {}
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Initialize all days with 0
            for i, day in enumerate(days):
                current_date = start_date + timedelta(days=i)
                daily_counts[day] = 0
            
            # Count meals per day
            for meal in meals:
                meal_date = datetime.fromisoformat(meal['meal_time'].replace('Z', '+00:00')).date()
                day_index = (meal_date - start_date).days
                if 0 <= day_index < 7:
                    day_name = days[day_index]
                    daily_counts[day_name] += 1
            
            return {
                'days': days,
                'meal_counts': [daily_counts[day] for day in days],
                'total_meals': sum(daily_counts.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly meal pattern for user {user_id}: {e}")
            return {'days': [], 'meal_counts': [], 'total_meals': 0}

    async def get_daily_meal_analysis(self, user_id: str) -> Dict[str, Any]:
        """Comprehensive analysis of all today's meals"""
        try:
            # Get today's meals
            today_meals = await self.get_today_meals(user_id)
            
            if not today_meals:
                return {
                    'has_meals': False,
                    'message': 'Log meals to receive personalized Ayurvedic guidance'
                }
            
            # Get recent mood
            recent_mood = await self._get_recent_mood(user_id)
            
            # Prepare meal summary for AI
            meal_summary = []
            for meal in today_meals:
                meal_info = f"{meal['meal_type'].capitalize()} ({meal.get('meal_time', '')}): {meal['meal_text']}"
                if meal.get('ingredients'):
                    meal_info += f" [Ingredients: {', '.join(meal['ingredients'][:5])}]"
                meal_summary.append(meal_info)
            
            meals_text = "\n".join(meal_summary)
            mood_context = ""
            if recent_mood:
                mood_context = f"\n\nCurrent mood: {recent_mood.get('emotion_type', 'neutral')} (intensity: {recent_mood.get('intensity', 5)}/10)"
            
            # Generate comprehensive analysis using Gemini
            prompt = f"""You are an Ayurvedic wellness expert. Analyze all meals eaten today and provide comprehensive guidance.

Today's Meals:
{meals_text}{mood_context}

Provide a detailed but concise analysis covering:

1. **Dosha Impact Summary**: How do today's meals affect Vata, Pitta, and Kapha? Which dosha is most increased or decreased?

2. **Healthiness Assessment**: Are the meals healthy overall? Describe if they are light/heavy, oily/dry, cooling/heating according to Ayurvedic principles.

3. **Ingredient Insights**: Highlight specific ingredients that positively or negatively affect digestion, mind, or energy levels.

4. **Mood-Based Interpretation**: How might these foods be influencing the current emotional state? What's the food-mood connection?

5. **Recommended Adjustments**: Provide specific, actionable improvements for the next meals. Include WHY each adjustment is important based on Ayurvedic principles. Be detailed but concise.

6. **Daily Balance Recommendation**: One clear, actionable sentence summarizing what to focus on for the rest of the day.

Return your analysis as a JSON object with these exact keys:
{{
  "dosha_impact": {{
    "summary": "Brief explanation of dosha effects",
    "primary_dosha": "vata|pitta|kapha",
    "effect": "increased|decreased|balanced"
  }},
  "healthiness": {{
    "overall_score": 70,
    "assessment": "Brief evaluation of healthiness",
    "qualities": ["light", "heating", "oily"]
  }},
  "ingredient_insights": {{
    "positive": ["ingredient1: specific benefit explained", "ingredient2: specific benefit explained"],
    "negative": ["ingredient1: specific concern explained", "ingredient2: specific concern explained"]
  }},
  "mood_interpretation": "How food relates to current mood with Ayurvedic reasoning",
  "adjustments": {{
    "next_meal_suggestions": [
      "Detailed suggestion 1 with reasoning",
      "Detailed suggestion 2 with reasoning",
      "Detailed suggestion 3 with reasoning"
    ],
    "foods_to_add": [
      "Food 1 - why it helps balance doshas or improve health",
      "Food 2 - why it helps balance doshas or improve health"
    ],
    "foods_to_reduce": [
      "Food 1 - why it aggravates doshas or harms health",
      "Food 2 - why it aggravates doshas or harms health"
    ]
  }},
  "daily_balance": "One actionable sentence with specific focus area"
}}

Keep all text concise and actionable. Be specific about Ayurvedic principles."""

            response = self.gemini.chat(prompt)
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            except Exception as e:
                logger.warning(f"Failed to parse Gemini JSON response: {e}")
                # Return fallback analysis
                analysis = self._get_fallback_daily_analysis(today_meals, recent_mood)
            
            # Add metadata
            analysis['has_meals'] = True
            analysis['meal_count'] = len(today_meals)
            analysis['analyzed_at'] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating daily meal analysis: {e}")
            return {
                'has_meals': False,
                'error': str(e),
                'message': 'Unable to generate analysis at this time'
            }

    def _get_fallback_daily_analysis(self, meals: List[Dict], mood: Optional[Dict]) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        meal_count = len(meals)
        
        # Determine time of day for contextual recommendations
        current_hour = datetime.now().hour
        time_context = "dinner" if current_hour >= 17 else "lunch" if current_hour >= 11 else "breakfast"
        
        return {
            "dosha_impact": {
                "summary": f"Based on {meal_count} meal(s) logged today, maintaining regular meal timing and warm, freshly prepared foods helps balance all three doshas naturally.",
                "primary_dosha": "vata",
                "effect": "balanced"
            },
            "healthiness": {
                "overall_score": 72,
                "assessment": "A balanced Ayurvedic diet emphasizes fresh, seasonal ingredients prepared with warming spices to enhance digestive fire (Agni).",
                "qualities": ["nourishing", "balanced"]
            },
            "ingredient_insights": {
                "positive": [
                    "Whole grains: Provide grounding energy and stabilize Vata dosha",
                    "Fresh vegetables: Enhance digestive fire and provide essential nutrients",
                    "Warming spices: Stimulate Agni and improve nutrient absorption"
                ],
                "negative": [
                    "Ensure adequate fiber intake to support healthy elimination",
                    "Stay well-hydrated with warm water throughout the day"
                ]
            },
            "mood_interpretation": "According to Ayurveda, balanced Agni (digestive fire) and regular meal timing create mental clarity and emotional stability by keeping all doshas in harmony.",
            "adjustments": {
                "next_meal_suggestions": [
                    f"For your next {time_context}, include dark leafy greens like spinach or kale to ground Vata and provide minerals",
                    "Add a high-quality protein source (lentils, mung beans, or paneer) to maintain steady energy and tissue building",
                    "Choose whole grains like quinoa or brown rice over refined grains to stabilize blood sugar and support digestion"
                ],
                "foods_to_add": [
                    "Leafy greens (spinach, kale) - Rich in minerals, cooling for Pitta, grounding for Vata",
                    "Nuts or seeds (almonds, pumpkin seeds) - Provide healthy fats and protein, nourish all tissues",
                    "Warming spices (ginger, cumin, turmeric) - Enhance digestion and reduce inflammation"
                ],
                "foods_to_reduce": [
                    "Processed foods - Lack prana (life force), increase Ama (toxins), and aggravate all doshas",
                    "Excess refined sugar - Spikes blood sugar, increases Kapha, and weakens digestive fire",
                    "Cold/raw foods in excess - Can dampen Agni and aggravate Vata"
                ]
            },
            "daily_balance": "Prioritize warm, freshly cooked meals with plenty of vegetables, whole grains, and digestive spices to maintain strong Agni and balanced doshas for the rest of the day."
        }

    async def get_daily_ayurveda_guidelines(self, user_id: str) -> Dict[str, Any]:
        """Get today's Ayurvedic guidelines based on meals"""
        try:
            today = date.today()
            
            result = self.supabase.table('meal_ayurveda_guidelines')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('date', today.isoformat())\
                .execute()
            
            guidelines = result.data or []
            
            # Organize by dosha and type
            organized = {
                'vata': {'avoid': [], 'favor': []},
                'pitta': {'avoid': [], 'favor': []},
                'kapha': {'avoid': [], 'favor': []},
                'balance': []
            }
            
            for guideline in guidelines:
                dosha = guideline.get('dosha_type', 'balance')
                g_type = guideline.get('guideline_type', 'balance')
                
                if dosha in organized and g_type in ['avoid', 'favor']:
                    organized[dosha][g_type].append(guideline['content'])
                else:
                    organized['balance'].append(guideline['content'])
            
            return organized
            
        except Exception as e:
            logger.error(f"Error getting daily guidelines for user {user_id}: {e}")
            return {'vata': {'avoid': [], 'favor': []}, 'pitta': {'avoid': [], 'favor': []}, 'kapha': {'avoid': [], 'favor': []}, 'balance': []}

    async def get_recipe_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get today's personalized recipe suggestions"""
        try:
            today = date.today()
            
            result = self.supabase.table('meal_recipe_suggestions')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('date', today.isoformat())\
                .order('created_at', desc=True)\
                .limit(6)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting recipe suggestions for user {user_id}: {e}")
            return []

    async def _extract_ingredients(self, meal_text: str) -> List[str]:
        """Extract ingredients from meal description using AI"""
        try:
            prompt = f"""
            Extract the main ingredients from this meal description: "{meal_text}"
            
            Return only a simple comma-separated list of ingredients, nothing else.
            Focus on the main food items, not cooking methods or adjectives.
            
            Example: "rice, chicken, vegetables, olive oil"
            """
            
            response = self.gemini.chat(prompt)
            
            # Check if response is an error message or chatbot refusal
            if any(phrase in response.lower() for phrase in [
                'apologize', 'unable to', 'cannot help', 'specifically designed',
                'mental wellness', 'error occurred'
            ]):
                logger.warning(f"Gemini returned error/refusal: {response[:100]}")
                raise Exception("Invalid Gemini response")
            
            # Clean and split the response
            ingredients = [ing.strip() for ing in response.split(',')]
            ingredients = [ing for ing in ingredients if ing and len(ing) > 1]
            
            # Additional validation - ingredients should be short food names
            ingredients = [ing for ing in ingredients if len(ing) < 50]
            
            return ingredients[:10] if ingredients else []
            
        except Exception as e:
            logger.warning(f"Failed to extract ingredients with AI: {e}")
            # Fallback: return empty list or meal_text as single item
            return [meal_text] if meal_text else []

    async def _analyze_dosha_impact(self, meal_text: str, ingredients: List[str]) -> Dict[str, Any]:
        """Analyze the dosha impact of a meal"""
        try:
            # AI analysis
            prompt = f"""
            Analyze this meal for Ayurvedic dosha impact: "{meal_text}"
            Ingredients: {', '.join(ingredients)}
            
            Determine which doshas (Vata, Pitta, Kapha) this meal affects and how.
            Return a JSON object with:
            - "vata": "increase" | "decrease" | "neutral"
            - "pitta": "increase" | "decrease" | "neutral"  
            - "kapha": "increase" | "decrease" | "neutral"
            - "primary_effect": the most significant dosha effect
            - "balance_recommendation": brief advice for balance
            
            Consider food qualities: hot/cold, heavy/light, oily/dry, sweet/bitter/spicy
            """
            
            response = self.gemini.chat(prompt)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response if wrapped in markdown
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1)
                elif '{' in response and '}' in response:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    response = response[start:end]
                
                impact = json.loads(response)
                return impact
                
            except json.JSONDecodeError:
                # Fallback analysis
                return self._simple_dosha_analysis(ingredients)
                
        except Exception as e:
            logger.warning(f"Failed to analyze dosha impact: {e}")
            return self._simple_dosha_analysis(ingredients)

    def _simple_dosha_analysis(self, ingredients: List[str]) -> Dict[str, Any]:
        """Simple rule-based dosha analysis"""
        vata_score = pitta_score = kapha_score = 0
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Vata impact
            if any(food in ingredient_lower for food in self.vata_pacifying):
                vata_score -= 1
            elif any(food in ingredient_lower for food in self.vata_aggravating):
                vata_score += 1
            
            # Pitta impact  
            if any(food in ingredient_lower for food in self.pitta_pacifying):
                pitta_score -= 1
            elif any(food in ingredient_lower for food in self.pitta_aggravating):
                pitta_score += 1
            
            # Kapha impact
            if any(food in ingredient_lower for food in self.kapha_pacifying):
                kapha_score -= 1
            elif any(food in ingredient_lower for food in self.kapha_aggravating):
                kapha_score += 1
        
        def score_to_effect(score):
            if score > 0:
                return "increase"
            elif score < 0:
                return "decrease" 
            else:
                return "neutral"
        
        effects = {
            "vata": score_to_effect(vata_score),
            "pitta": score_to_effect(pitta_score),
            "kapha": score_to_effect(kapha_score)
        }
        
        # Find primary effect
        scores = {"vata": abs(vata_score), "pitta": abs(pitta_score), "kapha": abs(kapha_score)}
        primary_dosha = max(scores, key=scores.get)
        effects["primary_effect"] = f"{primary_dosha}_{effects[primary_dosha]}"
        effects["balance_recommendation"] = "Include balancing foods in your next meal"
        
        return effects

    def _estimate_calories(self, meal_text: str, ingredients: List[str]) -> int:
        """Simple calorie estimation based on meal content"""
        base_calories = 200
        
        # Add calories based on ingredients
        high_cal_foods = ['rice', 'bread', 'oil', 'ghee', 'nuts', 'cheese', 'meat']
        medium_cal_foods = ['vegetables', 'fruits', 'dal', 'lentils']
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if any(food in ingredient_lower for food in high_cal_foods):
                base_calories += 150
            elif any(food in ingredient_lower for food in medium_cal_foods):
                base_calories += 50
        
        # Adjust based on meal type in text
        meal_lower = meal_text.lower()
        if any(word in meal_lower for word in ['large', 'big', 'heavy', 'full']):
            base_calories = int(base_calories * 1.3)
        elif any(word in meal_lower for word in ['small', 'light', 'little']):
            base_calories = int(base_calories * 0.7)
        
        return min(max(base_calories, 50), 1200)  # Cap between 50-1200 calories

    async def _generate_daily_guidelines(self, user_id: str, meal_id: str):
        """Generate comprehensive daily Ayurvedic guidelines based on today's meals and mood"""
        try:
            today = date.today()
            
            # Get today's meals to analyze overall pattern
            today_meals = await self.get_today_meals(user_id)
            
            if not today_meals:
                return
            
            # Get user's recent mood/emotion
            current_mood = await self._get_recent_mood(user_id)
            
            # Analyze overall dosha imbalance
            all_ingredients = []
            dosha_impacts = {'vata': 0, 'pitta': 0, 'kapha': 0}
            meal_descriptions = []
            
            for meal in today_meals:
                if meal.get('ingredients'):
                    all_ingredients.extend(meal['ingredients'])
                meal_descriptions.append(meal.get('meal_text', ''))
                
                impact_tags = meal.get('dosha_impact_tags', {})
                for dosha in ['vata', 'pitta', 'kapha']:
                    effect = impact_tags.get(dosha, 'neutral')
                    if effect == 'increase':
                        dosha_impacts[dosha] += 1
                    elif effect == 'decrease':
                        dosha_impacts[dosha] -= 1
            
            # Generate AI-powered comprehensive analysis
            ai_guidelines = await self._generate_ai_meal_analysis(
                meal_descriptions, 
                all_ingredients, 
                dosha_impacts,
                current_mood
            )
            
            # Also add traditional dosha-based guidelines
            traditional_guidelines = []
            for dosha, score in dosha_impacts.items():
                if score > 1:  # Dosha is aggravated
                    traditional_guidelines.extend(self._get_balancing_guidelines(dosha, 'aggravated'))
                elif score < -1:  # Dosha is depleted
                    traditional_guidelines.extend(self._get_balancing_guidelines(dosha, 'depleted'))
            
            # Combine AI and traditional guidelines
            all_guidelines = ai_guidelines + traditional_guidelines
            
            # Insert guidelines into database
            for guideline in all_guidelines:
                guideline_record = {
                    'id': str(uuid4()),
                    'user_id': user_id,
                    'date': today.isoformat(),
                    'meal_id': meal_id,
                    'guideline_type': guideline.get('type', 'general'),
                    'content': guideline['content'],
                    'dosha_type': guideline.get('dosha', 'general'),
                    'confidence_score': guideline.get('confidence', 0.8),
                    'created_at': datetime.now().isoformat()
                }
                
                # Check if similar guideline already exists today
                existing = self.supabase.table('meal_ayurveda_guidelines')\
                    .select('id')\
                    .eq('user_id', user_id)\
                    .eq('date', today.isoformat())\
                    .eq('content', guideline['content'])\
                    .execute()
                
                if not existing.data:
                    self.supabase.table('meal_ayurveda_guidelines')\
                        .insert(guideline_record)\
                        .execute()
            
            logger.info(f"Generated {len(all_guidelines)} guidelines for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error generating daily guidelines: {e}")

    async def _get_recent_mood(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's most recent mood/emotion"""
        try:
            result = self.supabase.table('emotion_logs')\
                .select('emotion_type, intensity, detected_at')\
                .eq('user_id', user_id)\
                .order('detected_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.warning(f"Failed to get recent mood: {e}")
            return None

    async def _generate_ai_meal_analysis(
        self, 
        meals: List[str], 
        ingredients: List[str],
        dosha_impacts: Dict[str, int],
        current_mood: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered meal analysis with health and mood-based guidance"""
        try:
            meal_summary = '; '.join(meals)
            ingredients_summary = ', '.join(set(ingredients))
            dosha_summary = ', '.join([f"{d}: {s}" for d, s in dosha_impacts.items()])
            
            mood_context = ""
            if current_mood:
                mood_type = current_mood.get('emotion_type', 'neutral')
                mood_intensity = current_mood.get('intensity', 0.5)
                mood_context = f"\n\nUser's current mood: {mood_type} (intensity: {mood_intensity})"
            
            prompt = f"""
            As an Ayurvedic nutritionist, analyze today's meals and provide personalized guidance.
            
            Today's Meals: {meal_summary}
            Ingredients: {ingredients_summary}
            Dosha Impact: {dosha_summary}{mood_context}
            
            Provide 4-6 specific, actionable guidelines covering:
            
            1. Health Analysis: Are these meals healthy? Nutritional balance assessment
            2. Dosha Balance: Specific foods to add or avoid based on dosha impacts
            3. Mood-Based Recommendations: Foods that can help improve/maintain their current mood
            4. Timing & Combinations: Suggestions for meal timing or food combinations
            5. Hydration & Lifestyle: Supporting wellness tips
            
            Return ONLY a JSON array with this exact structure:
            [
                {{
                    "type": "health" | "dosha" | "mood" | "general",
                    "content": "Specific, actionable guidance in one clear sentence",
                    "dosha": "vata" | "pitta" | "kapha" | "general",
                    "confidence": 0.7-1.0
                }}
            ]
            
            Make recommendations practical, specific, and tailored to their actual meals and mood.
            Each guideline should be a complete, clear sentence.
            """
            
            response = self.gemini.chat(prompt)
            
            try:
                # Extract JSON from response
                json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1)
                elif '[' in response and ']' in response:
                    start = response.find('[')
                    end = response.rfind(']') + 1
                    response = response[start:end]
                
                guidelines = json.loads(response)
                logger.info(f"Generated {len(guidelines)} AI-powered guidelines")
                return guidelines
                
            except json.JSONDecodeError as je:
                logger.warning(f"Failed to parse AI guidelines: {je}")
                # Return fallback guidelines
                return self._get_fallback_guidelines(dosha_impacts, current_mood)
                
        except Exception as e:
            logger.error(f"Error generating AI meal analysis: {e}")
            return self._get_fallback_guidelines(dosha_impacts, current_mood)

    def _get_fallback_guidelines(
        self, 
        dosha_impacts: Dict[str, int],
        current_mood: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate fallback guidelines when AI fails"""
        guidelines = []
        
        # Add health guideline
        guidelines.append({
            'type': 'health',
            'content': 'Your meals today show a good variety of nutrients. Continue maintaining this balance.',
            'dosha': 'general',
            'confidence': 0.7
        })
        
        # Add mood-based guideline if mood is available
        if current_mood:
            mood_type = current_mood.get('emotion_type', 'neutral')
            if mood_type in ['sadness', 'stress', 'anxiety']:
                guidelines.append({
                    'type': 'mood',
                    'content': 'Include warm, nourishing foods like soups and herbal teas to uplift your mood and calm your mind.',
                    'dosha': 'vata',
                    'confidence': 0.8
                })
            elif mood_type == 'anger':
                guidelines.append({
                    'type': 'mood',
                    'content': 'Choose cooling foods like cucumber, mint, and coconut to help calm your emotions and reduce heat.',
                    'dosha': 'pitta',
                    'confidence': 0.8
                })
            elif mood_type == 'joy':
                guidelines.append({
                    'type': 'mood',
                    'content': 'Your positive mood is great! Light, fresh foods will help maintain this uplifting energy.',
                    'dosha': 'general',
                    'confidence': 0.8
                })
        
        # Add dosha-specific guidelines
        dominant_dosha = max(dosha_impacts, key=lambda k: abs(dosha_impacts[k]))
        if abs(dosha_impacts[dominant_dosha]) > 0:
            if dosha_impacts[dominant_dosha] > 0:
                guidelines.append({
                    'type': 'dosha',
                    'content': f'Your {dominant_dosha} dosha shows signs of increase. Consider balancing with {dominant_dosha}-pacifying foods.',
                    'dosha': dominant_dosha,
                    'confidence': 0.75
                })
        
        return guidelines

    def _get_balancing_guidelines(self, dosha: str, state: str) -> List[Dict[str, Any]]:
        """Get balancing guidelines for a specific dosha state"""
        guidelines = []
        
        if dosha == 'vata':
            if state == 'aggravated':
                guidelines.extend([
                    {'type': 'avoid', 'content': 'Cold drinks, Raw vegetables, Dry snacks', 'dosha': 'vata', 'confidence': 0.9},
                    {'type': 'favor', 'content': 'Warm soups, Cooked grains, Sweet fruits', 'dosha': 'vata', 'confidence': 0.9}
                ])
            else:
                guidelines.extend([
                    {'type': 'favor', 'content': 'Light meals, Spices, Leafy greens', 'dosha': 'vata', 'confidence': 0.8}
                ])
        
        elif dosha == 'pitta':
            if state == 'aggravated':
                guidelines.extend([
                    {'type': 'avoid', 'content': 'Spicy food, Fried items, Citrus fruits', 'dosha': 'pitta', 'confidence': 0.9},
                    {'type': 'favor', 'content': 'Cooling foods, Sweet fruits, Coconut water', 'dosha': 'pitta', 'confidence': 0.9}
                ])
            else:
                guidelines.extend([
                    {'type': 'favor', 'content': 'Warm spices, Ginger, Light proteins', 'dosha': 'pitta', 'confidence': 0.8}
                ])
        
        elif dosha == 'kapha':
            if state == 'aggravated':
                guidelines.extend([
                    {'type': 'avoid', 'content': 'Heavy foods, Dairy products, Oily items', 'dosha': 'kapha', 'confidence': 0.9},
                    {'type': 'favor', 'content': 'Light meals, Spices, Leafy greens', 'dosha': 'kapha', 'confidence': 0.9}
                ])
            else:
                guidelines.extend([
                    {'type': 'favor', 'content': 'Nourishing soups, Whole grains, Healthy oils', 'dosha': 'kapha', 'confidence': 0.8}
                ])
        
        return guidelines

    async def _perform_comprehensive_meal_analysis(
        self,
        user_id: str,
        meal_id: str,
        meal_text: str,
        ingredients: List[str],
        dosha_impact: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive meal analysis using Gemini with mood integration"""
        try:
            # Get current mood
            current_mood = await self._get_recent_mood(user_id)
            
            mood_context = ""
            if current_mood:
                mood_type = current_mood.get('emotion_type', 'neutral')
                mood_intensity = current_mood.get('intensity', 0.5)
                mood_context = f"\nUser's Current Mood: {mood_type} (intensity: {mood_intensity:.2f})"
            
            # Create comprehensive analysis prompt
            prompt = f"""
            As an expert Ayurvedic nutritionist and wellness coach, analyze this meal comprehensively.
            
            Meal: {meal_text}
            Ingredients: {', '.join(ingredients)}
            Dosha Impact: Vata={dosha_impact.get('vata', 'neutral')}, Pitta={dosha_impact.get('pitta', 'neutral')}, Kapha={dosha_impact.get('kapha', 'neutral')}{mood_context}
            
            Provide a detailed analysis covering:
            
            1. HEALTH ASSESSMENT
               - Is this meal healthy or unhealthy? Why?
               - Nutritional strengths and weaknesses
               - Portion size assessment
            
            2. AYURVEDIC ANALYSIS - ONLY 3 KEY POINTS
               Keep this section BRIEF and CONCISE:
               - Point 1: Dosha effect (1 sentence: which dosha is affected and how)
               - Point 2: Constitution impact (1 sentence: immediate body effect)  
               - Point 3: Timing consideration (1 sentence: is this meal appropriate for time of day)
               
               DO NOT write paragraphs. Keep each point to ONE SHORT sentence (10-15 words max).
            
            3. MOOD-BASED RECOMMENDATIONS
               - How this meal may affect the user's current mood
               - Foods to add or modify to improve emotional well-being
               - Specific ingredients that support mental health
            
            4. FOOD ALTERNATIVES & IMPROVEMENTS
               - Better food choices or substitutions
               - Healthier cooking methods
               - Complementary foods to add
            
            5. AYURVEDIC GUIDANCE - EXACTLY 2 FOOD TIPS
               Provide ONLY 2 specific, actionable food tips to improve health instead of current meal:
               
               Tip 1: One healthier food alternative to what was eaten (be specific)
               Tip 2: One beneficial food to add in next meal (be specific)
               
               Format: Short, direct recommendations (1 sentence each)
               Example: "Replace white rice with quinoa for better protein" OR "Add steamed spinach to your next meal for iron"
               
               DO NOT include: lifestyle tips, general advice, or foods to avoid
               ONLY include: 2 specific food tips for healthier alternatives
            
            Return ONLY a JSON object with this structure:
            {{
                "health_assessment": {{
                    "is_healthy": true/false,
                    "health_score": 0-100,
                    "summary": "Brief health verdict",
                    "strengths": ["strength1", "strength2"],
                    "concerns": ["concern1", "concern2"]
                }},
                "ayurvedic_analysis": {{
                    "point1": "Dosha effect (1 short sentence)",
                    "point2": "Constitution impact (1 short sentence)",
                    "point3": "Timing advice (1 short sentence)"
                }},
                "mood_recommendations": {{
                    "mood_impact": "How meal affects current mood",
                    "foods_to_add": ["food1", "food2"],
                    "mental_health_benefits": "Specific benefits"
                }},
                "alternatives": {{
                    "better_choices": ["option1", "option2"],
                    "cooking_methods": ["method1", "method2"],
                    "complementary_foods": ["food1", "food2"]
                }},
                "guidance": {{
                    "food_tip_1": "Specific healthier alternative to current food",
                    "food_tip_2": "Specific beneficial food to add next meal"
                }}
            }}
            """
            
            response = self.gemini.chat(prompt)
            
            # Parse JSON response
            try:
                json_match = re.search(r'```json\s*(\{{.*?\}})\s*```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1)
                elif '{' in response and '}' in response:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    response = response[start:end]
                
                analysis = json.loads(response)
                
                # Store analysis in database for future reference
                analysis_record = {
                    'id': str(uuid4()),
                    'meal_id': meal_id,
                    'user_id': user_id,
                    'analysis_data': analysis,
                    'mood_at_analysis': current_mood.get('emotion_type') if current_mood else None,
                    'created_at': datetime.now().isoformat()
                }
                
                # Note: You may need to create a meal_analysis table
                # For now, we'll just return the analysis
                
                logger.info(f"Generated comprehensive analysis for meal {meal_id}")
                return analysis
                
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse Gemini analysis: {je}")
                return self._get_fallback_analysis(meal_text, current_mood)
                
        except Exception as e:
            logger.error(f"Error in comprehensive meal analysis: {e}")
            return self._get_fallback_analysis(meal_text, current_mood)

    def _get_fallback_analysis(self, meal_text: str, current_mood: Optional[Dict]) -> Dict[str, Any]:
        """Fallback analysis when Gemini fails"""
        return {
            "health_assessment": {
                "is_healthy": True,
                "health_score": 70,
                "summary": "Include more vegetables and whole grains for optimal nutrition.",
                "strengths": ["Provides energy"],
                "concerns": ["Add more fiber"]
            },
            "ayurvedic_analysis": {
                "point1": "Balanced effect on all three doshas.",
                "point2": "Supports vitality and energy levels.",
                "point3": "Best consumed during main meal times."
            },
            "mood_recommendations": {
                "mood_impact": "Balanced nutrition supports emotional well-being.",
                "foods_to_add": ["Leafy greens", "Nuts", "Berries"],
                "mental_health_benefits": "Wholesome foods promote mental clarity."
            },
            "alternatives": {
                "better_choices": ["Add whole grains", "Include vegetables"],
                "cooking_methods": ["Steam", "Sauté"],
                "complementary_foods": ["Herbal tea", "Fresh fruit"]
            },
            "guidance": {
                "food_tip_1": "Replace refined grains with whole grain alternatives like brown rice or quinoa",
                "food_tip_2": "Add a serving of colorful vegetables to your next meal for vitamins"
            }
        }

    async def _create_mood_meal_correlation(self, user_id: str, meal_id: str):
        """Create correlation between meal and current mood"""
        try:
            # Get current mood
            current_mood = await self._get_recent_mood(user_id)
            
            if not current_mood:
                logger.info(f"No mood data found for user {user_id}, skipping correlation")
                return
            
            # Get the meal details
            meal_result = self.supabase.table('meals').select('*').eq('id', meal_id).execute()
            
            if not meal_result.data:
                return
            
            meal = meal_result.data[0]
            
            # Create correlation record
            correlation_record = {
                'id': str(uuid4()),
                'user_id': user_id,
                'meal_id': meal_id,
                'emotion_type': current_mood.get('emotion_type'),
                'emotion_intensity': current_mood.get('intensity', 0.5),
                'meal_type': meal.get('meal_type'),
                'ingredients': meal.get('ingredients', []),
                'dosha_impact': meal.get('dosha_impact_tags', {}),
                'correlation_score': await self._calculate_mood_correlation(
                    meal.get('ingredients', []),
                    current_mood.get('emotion_type')
                ),
                'created_at': datetime.now().isoformat()
            }
            
            self.supabase.table('meal_emotion_correlations').insert(correlation_record).execute()
            logger.info(f"Created mood-meal correlation for meal {meal_id}")
            
        except Exception as e:
            logger.error(f"Error creating mood-meal correlation: {e}")

    async def _calculate_mood_correlation(self, ingredients: List[str], emotion_type: str) -> float:
        """Calculate correlation score between ingredients and mood"""
        # Mood-boosting foods
        mood_boosting = ['banana', 'nuts', 'dark chocolate', 'berries', 'salmon', 'avocado', 
                         'spinach', 'yogurt', 'oats', 'turmeric', 'green tea']
        
        calming_foods = ['chamomile', 'warm milk', 'honey', 'almonds', 'turkey', 'sweet potato']
        
        energizing_foods = ['coffee', 'green tea', 'ginger', 'citrus', 'whole grains']
        
        score = 0.5  # baseline
        
        ingredient_lower = [ing.lower() for ing in ingredients]
        
        # Positive emotions (joy, happiness)
        if emotion_type in ['joy', 'happiness', 'contentment']:
            for ing in ingredient_lower:
                if any(food in ing for food in mood_boosting):
                    score += 0.1
            score = min(score, 0.95)
        
        # Negative emotions (sadness, anxiety, stress)
        elif emotion_type in ['sadness', 'anxiety', 'stress', 'fear']:
            for ing in ingredient_lower:
                if any(food in ing for food in calming_foods):
                    score += 0.15
                elif any(food in ing for food in mood_boosting):
                    score += 0.1
            score = min(score, 0.9)
        
        # Low energy emotions
        elif emotion_type in ['fatigue', 'lethargy']:
            for ing in ingredient_lower:
                if any(food in ing for food in energizing_foods):
                    score += 0.12
            score = min(score, 0.88)
        
        return round(score, 2)

    async def _generate_recipe_suggestions(self, user_id: str):
        """Generate personalized recipe suggestions based on today's meals"""
        try:
            today = date.today()
            
            # Get today's meals and dosha analysis
            today_meals = await self.get_today_meals(user_id)
            guidelines = await self.get_daily_ayurveda_guidelines(user_id)
            
            # Generate recipe suggestions using AI
            meal_summary = ', '.join([meal['meal_text'] for meal in today_meals[-3:]])  # Last 3 meals
            
            prompt = f"""
            Based on today's meals: {meal_summary}
            
            Generate 3 personalized Ayurvedic recipe suggestions that would balance the user's current dietary pattern.
            
            Return JSON array with recipes having:
            - "name": recipe name
            - "description": brief description and benefits
            - "prep_time": preparation time in minutes
            - "ingredients": array of main ingredients
            - "dosha_benefits": which doshas this recipe balances
            - "benefits": array of health benefits
            
            Focus on simple, practical recipes that complement what they've already eaten.
            """
            
            response = self.gemini.chat(prompt)
            
            try:
                # Extract JSON from response
                json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
                if json_match:
                    response = json_match.group(1)
                elif '[' in response and ']' in response:
                    start = response.find('[')
                    end = response.rfind(']') + 1
                    response = response[start:end]
                
                recipes = json.loads(response)
                
                # Insert recipes into database
                for recipe in recipes:
                    recipe_record = {
                        'id': str(uuid4()),
                        'user_id': user_id,
                        'date': today.isoformat(),
                        'recipe_name': recipe.get('name', 'Ayurvedic Recipe'),
                        'recipe_description': recipe.get('description', ''),
                        'prep_time_minutes': recipe.get('prep_time', 30),
                        'ingredients': recipe.get('ingredients', []),
                        'dosha_balance_tags': recipe.get('dosha_benefits', {}),
                        'benefits': recipe.get('benefits', []),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Check if recipe already exists today
                    existing = self.supabase.table('meal_recipe_suggestions')\
                        .select('id')\
                        .eq('user_id', user_id)\
                        .eq('date', today.isoformat())\
                        .eq('recipe_name', recipe.get('name', 'Ayurvedic Recipe'))\
                        .execute()
                    
                    if not existing.data:
                        self.supabase.table('meal_recipe_suggestions')\
                            .insert(recipe_record)\
                            .execute()
                
                logger.info(f"Generated {len(recipes)} recipe suggestions for user {user_id}")
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse recipe suggestions from AI response")
                
        except Exception as e:
            logger.error(f"Error generating recipe suggestions: {e}")

# Create a global instance
meal_service = MealService()
