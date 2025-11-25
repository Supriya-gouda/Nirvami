"""
Wearable Integration Service
Handles data from smartwatches and manual entry, aggregation, and recommendations.
"""
import logging
import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)


class WearableService:
    """Service for wearable data ingestion, aggregation, and analysis."""
    
    @staticmethod
    def ingest_watch_data(user_id: str, data: Dict[str, Any]) -> Dict:
        """
        Ingest data from a smartwatch and analyze for health anomalies.
        
        Args:
            user_id: User ID
            data: Watch data payload
                {
                    "provider": "apple_watch" | "fitbit" | ...,
                    "captured_at": "2025-11-24T06:30:00Z",
                    "heart_rate": 78,
                    "hrv_ms": 65,
                    "steps": 4500,
                    "sleep_hours": 7.2,
                    "stress_level": 4,
                    "active_calories": 320
                }
        
        Returns:
            Created snapshot record
        """
        try:
            supabase = get_supabase()
            
            # Parse captured_at
            if isinstance(data.get("captured_at"), str):
                captured_at = datetime.fromisoformat(data["captured_at"].replace("Z", "+00:00"))
            else:
                captured_at = data.get("captured_at", datetime.now())
            
            snapshot = {
                "user_id": user_id,
                "source": "watch",
                "provider": data.get("provider", "unknown"),
                "captured_at": captured_at.isoformat(),
                "heart_rate": data.get("heart_rate"),
                "hrv_ms": data.get("hrv_ms"),
                "steps": data.get("steps"),
                "sleep_hours": data.get("sleep_hours"),
                "stress_level": data.get("stress_level"),
                "active_calories": data.get("calories_burned") or data.get("active_calories"),
                "raw_payload": data
            }
            
            result = supabase.table("wearable_snapshots").insert(snapshot).execute()
            
            if result.data:
                snapshot_record = result.data[0]
                logger.info(f"Ingested watch data for user {user_id} from {data.get('provider')}")
                return snapshot_record
            else:
                raise Exception("Failed to insert wearable snapshot")
                
        except Exception as e:
            logger.error(f"Error ingesting watch data: {e}")
            raise
    
    @staticmethod
    def ingest_manual_entry(user_id: str, data: Dict[str, Any]) -> Dict:
        """
        Ingest manually entered health data and analyze for health anomalies.
        
        Args:
            user_id: User ID
            data: Manual entry data
                {
                    "date": "2025-11-23",
                    "sleep_hours": 6.5,
                    "avg_heart_rate": 85,
                    "steps": 3200,
                    "stress_level": 7
                }
        
        Returns:
            Created snapshot record
        """
        try:
            # Use service role to bypass RLS
            supabase = get_supabase(use_service_role=True)
            
            # Convert date to synthetic captured_at (date + 23:00)
            entry_date = date.fromisoformat(data["date"]) if isinstance(data.get("date"), str) else data.get("date", date.today())
            captured_at = datetime.combine(entry_date, datetime.min.time().replace(hour=23))
            timestamp_iso = captured_at.isoformat()
            
            snapshot = {
                "user_id": user_id,
                "source": "manual",
                "provider": "manual_form",
                "captured_at": timestamp_iso,
                "recorded_at": timestamp_iso,  # Required for backward compatibility
                "heart_rate": data.get("avg_heart_rate") or data.get("heart_rate"),
                "hrv_ms": data.get("hrv_ms"),
                "steps": data.get("steps"),
                "sleep_hours": data.get("sleep_hours"),
                "stress_level": data.get("stress_level"),
                "calories_burned": data.get("calories_burned"),
                "active_calories": data.get("active_calories"),
                "raw_payload": data
            }
            
            logger.info(f"Inserting manual entry for user {user_id}: {snapshot}")
            result = supabase.table("wearable_snapshots").insert(snapshot).execute()
            
            if result.data:
                snapshot_record = result.data[0]
                logger.info(f"✅ Ingested manual entry for user {user_id} for date {entry_date}")
                return snapshot_record
            else:
                logger.error("No data returned from insert")
                raise Exception("Failed to insert manual entry - no data returned")
                
        except Exception as e:
            logger.error(f"❌ Error ingesting manual entry: {e}", exc_info=True)
            raise
    
    @staticmethod
    def aggregate_daily_stats(user_id: str, target_date: Optional[date] = None) -> Dict:
        """
        Aggregate wearable_snapshots into daily stats for a specific date.
        
        Args:
            user_id: User ID
            target_date: Date to aggregate (default: yesterday)
        
        Returns:
            Aggregated daily stats record
        """
        try:
            # Use service role to bypass RLS
            supabase = get_supabase(use_service_role=True)
            
            if target_date is None:
                target_date = date.today() - timedelta(days=1)
            
            # Fetch all snapshots for this date
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = datetime.combine(target_date, datetime.max.time())
            
            snapshots_result = supabase.table("wearable_snapshots").select("*").eq(
                "user_id", user_id
            ).gte("captured_at", start_time.isoformat()).lte(
                "captured_at", end_time.isoformat()
            ).execute()
            
            if not snapshots_result.data:
                logger.info(f"No snapshots found for user {user_id} on {target_date}")
                return {"message": "No data to aggregate"}
            
            snapshots = snapshots_result.data
            
            # Compute aggregates
            heart_rates = [s["heart_rate"] for s in snapshots if s.get("heart_rate")]
            hrv_values = [s["hrv_ms"] for s in snapshots if s.get("hrv_ms")]
            steps_values = [s["steps"] for s in snapshots if s.get("steps")]
            sleep_values = [s["sleep_hours"] for s in snapshots if s.get("sleep_hours")]
            stress_values = [s["stress_level"] for s in snapshots if s.get("stress_level")]
            
            # Determine data source
            sources = set(s["source"] for s in snapshots)
            if len(sources) == 1:
                data_source = list(sources)[0]
            else:
                data_source = "mixed"
            
            daily_stats = {
                "user_id": user_id,
                "date": target_date.isoformat(),
                "avg_heart_rate": round(sum(heart_rates) / len(heart_rates), 2) if heart_rates else None,
                "min_heart_rate": min(heart_rates) if heart_rates else None,
                "max_heart_rate": max(heart_rates) if heart_rates else None,
                "avg_hrv_ms": round(sum(hrv_values) / len(hrv_values), 2) if hrv_values else None,
                "total_steps": sum(steps_values) if steps_values else None,
                "sleep_hours": round(max(sleep_values), 2) if sleep_values else None,  # Use max or average
                "avg_stress_level": round(sum(stress_values) / len(stress_values), 2) if stress_values else None,
                "data_source": data_source,
                "updated_at": datetime.now().isoformat()
            }
            
            # Upsert (insert or update)
            result = supabase.table("wearable_daily_stats").upsert(
                daily_stats,
                on_conflict="user_id,date"
            ).execute()
            
            if result.data:
                logger.info(f"Aggregated daily stats for user {user_id} on {target_date}")
                return result.data[0]
            else:
                raise Exception("Failed to upsert daily stats")
                
        except Exception as e:
            logger.error(f"Error aggregating daily stats: {e}")
            raise
    
    @staticmethod
    def detect_emotion_from_wearables(user_id: str, daily_stats: Dict) -> Optional[Dict]:
        """
        Detect emotion/stress from wearable data using rule-based logic.
        
        Args:
            user_id: User ID
            daily_stats: Daily stats dictionary
        
        Returns:
            Emotion log entry to insert, or None
        """
        try:
            sleep_hours = daily_stats.get("sleep_hours", 7)
            avg_stress = daily_stats.get("avg_stress_level", 5)
            avg_hr = daily_stats.get("avg_heart_rate", 70)
            avg_hrv = daily_stats.get("avg_hrv_ms", 60)
            
            emotion_type = None
            confidence = 0.0
            factors = {}
            
            # Rule 1: High stress detection
            if (sleep_hours and sleep_hours < 6) or (avg_stress and avg_stress >= 7) or (avg_hr and avg_hr > 90):
                emotion_type = "stressed"
                confidence = 0.75
                
                if sleep_hours and sleep_hours < 6:
                    factors["sleep_factor"] = 0.8
                if avg_stress and avg_stress >= 7:
                    factors["stress_factor"] = 0.9
                if avg_hr and avg_hr > 90:
                    factors["heart_rate_factor"] = 0.7
                
            # Rule 2: Calm/balanced detection
            elif (sleep_hours and sleep_hours >= 7) and (avg_hrv and avg_hrv > 60) and (avg_stress and avg_stress <= 3):
                emotion_type = "calm"
                confidence = 0.80
                factors["sleep_factor"] = 0.8
                factors["hrv_factor"] = 0.7
                factors["stress_factor"] = 0.9
            
            # Rule 3: Fatigued detection
            elif sleep_hours and sleep_hours < 5:
                emotion_type = "fatigued"
                confidence = 0.70
                factors["sleep_factor"] = 0.9
            
            # Rule 4: Anxious detection
            elif (avg_hr and avg_hr > 85) and (avg_stress and avg_stress >= 6):
                emotion_type = "anxious"
                confidence = 0.65
                factors["heart_rate_factor"] = 0.7
                factors["stress_factor"] = 0.8
            
            if emotion_type:
                emotion_log = {
                    "user_id": user_id,
                    "emotion_type": emotion_type,
                    "confidence": confidence,
                    "source": "wearable",
                    "all_scores": {
                        "wearable_inference": confidence,
                        **factors
                    },
                    "created_at": datetime.now().isoformat()
                }
                
                return emotion_log
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting emotion from wearables: {e}")
            return None
    
    @staticmethod
    def get_food_recommendations(daily_stats: Dict, dosha_type: Optional[str] = None) -> List[Dict]:
        """
        Get food recommendations based on wearable stats.
        
        Args:
            daily_stats: Daily stats dictionary
            dosha_type: User's dosha type (optional)
        
        Returns:
            List of food recommendation dictionaries
        """
        try:
            supabase = get_supabase()
            recommendations = []
            tags = []
            
            sleep_hours = daily_stats.get("sleep_hours", 7)
            avg_stress = daily_stats.get("avg_stress_level", 5)
            total_steps = daily_stats.get("total_steps", 0)
            
            # Map conditions to tags
            if sleep_hours and sleep_hours < 6:
                tags.extend(["sleep_support", "calming"])
                recommendations.append({
                    "reason": "Low sleep detected",
                    "suggestion": "Light, warm foods; avoid caffeine after 5pm",
                    "foods": ["Warm milk with turmeric", "Chamomile tea", "Almonds"]
                })
            
            if avg_stress and avg_stress >= 7:
                tags.extend(["stress_relief", "calming"])
                recommendations.append({
                    "reason": "High stress levels",
                    "suggestion": "Stress-reducing foods rich in magnesium",
                    "foods": ["Dark leafy greens", "Bananas", "Dark chocolate (in moderation)"]
                })
            
            if total_steps and total_steps > 10000:
                tags.extend(["energy", "recovery"])
                recommendations.append({
                    "reason": "High activity detected",
                    "suggestion": "Balanced carbs and protein for recovery",
                    "foods": ["Quinoa bowl", "Grilled chicken", "Sweet potato", "Electrolyte water"]
                })
            
            # Query ayurveda_resources if available
            if tags:
                try:
                    resources = supabase.table("ayurveda_resources").select("*").execute()
                    if resources.data:
                        # Filter by tags (simplified - you can make this more sophisticated)
                        for resource in resources.data[:3]:
                            if resource.get("category") == "food":
                                recommendations.append({
                                    "reason": "Ayurvedic recommendation",
                                    "suggestion": resource.get("title"),
                                    "foods": resource.get("practices", [])
                                })
                except Exception as e:
                    logger.debug(f"Could not fetch ayurveda resources: {e}")
            
            return recommendations[:3]  # Return top 3
            
        except Exception as e:
            logger.error(f"Error getting food recommendations: {e}")
            return []
    
    @staticmethod
    def get_yoga_recommendations(daily_stats: Dict, dosha_type: Optional[str] = None) -> List[Dict]:
        """
        Get yoga recommendations based on wearable stats.
        
        Args:
            daily_stats: Daily stats dictionary
            dosha_type: User's dosha type (optional)
        
        Returns:
            List of yoga recommendation dictionaries
        """
        try:
            supabase = get_supabase()
            recommendations = []
            tags = []
            
            avg_stress = daily_stats.get("avg_stress_level", 5)
            avg_hr = daily_stats.get("avg_heart_rate", 70)
            total_steps = daily_stats.get("total_steps", 0)
            
            # Map conditions to tags
            if avg_stress and avg_stress >= 7 or (avg_hr and avg_hr > 85):
                tags.extend(["relaxation", "stress_relief", "anxiety"])
                recommendations.append({
                    "reason": "High stress/heart rate detected",
                    "practice": "Calming breathwork and restorative poses",
                    "poses": ["Child's Pose", "Legs Up the Wall", "Corpse Pose", "Alternate Nostril Breathing"]
                })
            
            if total_steps and total_steps < 3000:
                tags.extend(["energy", "activation"])
                recommendations.append({
                    "reason": "Low activity detected",
                    "practice": "Energizing yoga sequence",
                    "poses": ["Sun Salutations", "Warrior poses", "Triangle Pose", "Backbends"]
                })
            
            # Query yoga_poses table if available
            if tags:
                try:
                    # Build query with tag filtering
                    yoga_query = supabase.table("yoga_poses").select("*").limit(5)
                    
                    if dosha_type:
                        # Could add dosha filtering here
                        pass
                    
                    yoga_result = yoga_query.execute()
                    
                    if yoga_result.data:
                        for pose in yoga_result.data[:2]:
                            recommendations.append({
                                "reason": "Recommended yoga practice",
                                "practice": pose.get("name"),
                                "poses": pose.get("steps", []),
                                "duration": pose.get("duration")
                            })
                except Exception as e:
                    logger.debug(f"Could not fetch yoga poses: {e}")
            
            return recommendations[:3]  # Return top 3
            
        except Exception as e:
            logger.error(f"Error getting yoga recommendations: {e}")
            return []
    
    @staticmethod
    def get_today_summary(user_id: str, target_date: Optional[date] = None) -> Dict:
        """
        Get comprehensive wearable summary with recommendations.
        
        Args:
            user_id: User ID
            target_date: Date to summarize (default: today)
        
        Returns:
            Complete summary dictionary
        """
        try:
            supabase = get_supabase()
            
            if target_date is None:
                target_date = date.today()
            
            # Get daily stats
            stats_result = supabase.table("wearable_daily_stats").select("*").eq(
                "user_id", user_id
            ).eq("date", target_date.isoformat()).execute()
            
            if not stats_result.data:
                # Try to aggregate on-the-fly
                try:
                    daily_stats = WearableService.aggregate_daily_stats(user_id, target_date)
                except:
                    return {
                        "date": target_date.isoformat(),
                        "message": "No wearable data available for this date",
                        "has_data": False
                    }
            else:
                daily_stats = stats_result.data[0]
            
            # Get user profile for dosha
            profile_result = supabase.table("profiles").select("dosha_type").eq("id", user_id).execute()
            dosha_type = profile_result.data[0].get("dosha_type") if profile_result.data else None
            
            # Detect emotion
            inferred_emotion = WearableService.detect_emotion_from_wearables(user_id, daily_stats)
            emotion_type = inferred_emotion["emotion_type"] if inferred_emotion else "balanced"
            
            # Store detected emotion
            if inferred_emotion:
                try:
                    supabase.table("emotion_logs").insert(inferred_emotion).execute()
                except Exception as e:
                    logger.debug(f"Could not store inferred emotion: {e}")
            
            # Get recommendations
            food_recs = WearableService.get_food_recommendations(daily_stats, dosha_type)
            yoga_recs = WearableService.get_yoga_recommendations(daily_stats, dosha_type)
            
            return {
                "date": target_date.isoformat(),
                "has_data": True,
                "sleep_hours": daily_stats.get("sleep_hours"),
                "avg_heart_rate": daily_stats.get("avg_heart_rate"),
                "steps": daily_stats.get("total_steps"),  # Map total_steps to steps for frontend
                "total_steps": daily_stats.get("total_steps"),
                "avg_stress_level": daily_stats.get("avg_stress_level"),
                "data_source": daily_stats.get("data_source"),
                "inferred_emotion": emotion_type,
                "food_recommendations": food_recs,
                "yoga_recommendations": yoga_recs,
                "insights": WearableService._generate_insights(daily_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting today summary: {e}")
            raise
    
    @staticmethod
    def _generate_insights(daily_stats: Dict) -> List[str]:
        """Generate human-readable insights from daily stats."""
        insights = []
        
        sleep_hours = daily_stats.get("sleep_hours")
        if sleep_hours:
            if sleep_hours < 6:
                insights.append(f"⚠️ Low sleep: {sleep_hours:.1f} hrs - Aim for 7-9 hours")
            elif sleep_hours >= 8:
                insights.append(f"✅ Great sleep: {sleep_hours:.1f} hrs")
            else:
                insights.append(f"😊 Decent sleep: {sleep_hours:.1f} hrs")
        
        avg_hr = daily_stats.get("avg_heart_rate")
        if avg_hr:
            if avg_hr > 90:
                insights.append(f"⚠️ Elevated heart rate: {avg_hr:.0f} bpm - Consider relaxation")
            elif avg_hr < 60:
                insights.append(f"✅ Low resting heart rate: {avg_hr:.0f} bpm - Good fitness")
            else:
                insights.append(f"Heart rate: {avg_hr:.0f} bpm")
        
        steps = daily_stats.get("total_steps")
        if steps:
            if steps >= 10000:
                insights.append(f"🎉 Excellent activity: {steps:,} steps!")
            elif steps >= 6000:
                insights.append(f"✅ Good activity: {steps:,} steps")
            else:
                insights.append(f"💪 Try to walk more: {steps:,} steps - Aim for 6,000+")
        
        stress = daily_stats.get("avg_stress_level")
        if stress:
            if stress >= 7:
                insights.append(f"⚠️ High stress detected: {stress:.1f}/10 - Practice mindfulness")
            elif stress <= 3:
                insights.append(f"✅ Low stress: {stress:.1f}/10 - Well balanced!")
        
        return insights
