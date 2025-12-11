"""Simplified Wearable Service - Clean implementation matching new schema."""
import logging
from datetime import date, datetime
from typing import Dict, Any, Optional, List
from app.utils.database import get_supabase

logger = logging.getLogger(__name__)


class WearableService:
    """Service for managing wearable health data."""
    
    @staticmethod
    def save_manual_entry(user_id: str, data: Dict[str, Any], source: str = "manual") -> Dict:
        """
        Save health data entry (manual or from device).
        
        Args:
            user_id: User ID
            data: {
                "date": "2025-11-25",
                "sleep_hours": 7.5,
                "avg_heart_rate": 72,
                "steps": 8000,
                "stress_level": 5,
                "calories_burned": 350,
                "source": "manual" or "watch" (optional, overridden by source param)
            }
            source: Data source - "manual" for manual entry, "watch" for Apple Health XML
        
        Returns:
            Saved snapshot record
        """
        try:
            # Use service role to bypass RLS
            supabase = get_supabase(use_service_role=True)
            
            # Prepare snapshot data
            # Always use the source parameter (it takes priority over data['source'])
            data_source = source
            
            snapshot = {
                "user_id": user_id,
                "date": data.get("date"),
                "source": data_source,
                "sleep_hours": data.get("sleep_hours"),
                "avg_heart_rate": data.get("avg_heart_rate"),
                "steps": data.get("steps"),
                "stress_level": data.get("stress_level"),
                "calories_burned": data.get("calories_burned"),
                "hrv_ms": data.get("hrv_ms")
            }
            
            # Remove None values
            snapshot = {k: v for k, v in snapshot.items() if v is not None}
            
            logger.info(f"💾 Attempting to save entry for user={user_id}, date={data.get('date')}, source={data_source}")
            logger.info(f"📊 Snapshot to save: {snapshot}")
            
            # Upsert (insert or update if exists)
            result = supabase.table("wearable_snapshots")\
                .upsert(snapshot, on_conflict="user_id,date,source")\
                .execute()
            
            logger.info(f"📤 Database response: {result}")
            
            if result.data:
                logger.info(f"✅ Successfully saved wearable data: {result.data[0]}")
                return result.data[0]
            else:
                logger.error(f"❌ No data returned from upsert. Full result: {result}")
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"❌ Error saving manual entry: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_latest(user_id: str) -> Optional[Dict]:
        """Get the most recent wearable entry for a user."""
        try:
            supabase = get_supabase(use_service_role=True)
            
            result = supabase.table("wearable_snapshots")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("date", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching latest wearable data: {e}")
            return None
    
    @staticmethod
    def get_all_for_user(user_id: str, limit: int = 30) -> List[Dict]:
        """Get all wearable entries for a user."""
        try:
            supabase = get_supabase(use_service_role=True)
            
            result = supabase.table("wearable_snapshots")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("date", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error fetching wearable data: {e}")
            return []
    
    @staticmethod
    def analyze_health_risks(user_id: str) -> Dict:
        """
        Analyze wearable data for health risks.
        
        Returns:
            {
                "has_risks": bool,
                "risk_level": "low" | "medium" | "high" | "critical",
                "risks": [...],
                "recommendations": [...],
                "data": {...}
            }
        """
        try:
            # Get latest entry
            latest = WearableService.get_latest(user_id)
            
            if not latest:
                return {
                    "has_risks": False,
                    "risk_level": "none",
                    "risks": [],
                    "recommendations": ["📊 No data available. Please log your health metrics."],
                    "data": None
                }
            
            risks = []
            recommendations = []
            risk_level = "low"
            
            sleep_hours = latest.get("sleep_hours")
            heart_rate = latest.get("avg_heart_rate")
            steps = latest.get("steps")
            stress_level = latest.get("stress_level")
            hrv_ms = latest.get("hrv_ms")
            
            # 1️⃣ Very High Resting Heart Rate (>90 bpm)
            if heart_rate:
                if heart_rate >= 120:
                    risks.append(f"🚨 CRITICAL: Extremely high heart rate ({heart_rate} bpm)")
                    risk_level = "critical"
                    recommendations.extend([
                        "🏥 Seek immediate medical attention",
                        "💨 Practice deep breathing exercises",
                        "🛑 Stop any strenuous activity"
                    ])
                elif heart_rate >= 100:
                    risks.append(f"⚠️ Very high heart rate ({heart_rate} bpm)")
                    risk_level = "high" if risk_level != "critical" else risk_level
                    recommendations.extend([
                        "💧 Stay hydrated",
                        "☕ Avoid caffeine",
                        "🧘 Practice relaxation techniques"
                    ])
                elif heart_rate >= 90:
                    risks.append(f"⚡ Elevated resting heart rate ({heart_rate} bpm)")
                    risk_level = "medium" if risk_level == "low" else risk_level
                    recommendations.extend([
                        "💧 Drink plenty of water",
                        "💨 Try breathing exercises (4-7-8 technique)",
                        "😴 Ensure adequate rest"
                    ])
            
            # 2️⃣ Low Sleep Duration
            if sleep_hours is not None:
                if sleep_hours < 4:
                    risks.append(f"🚨 CRITICAL: Severe sleep deprivation ({sleep_hours:.1f} hours)")
                    risk_level = "critical"
                    recommendations.extend([
                        "😴 URGENT: Prioritize sleep immediately",
                        "🛌 Take a power nap if possible",
                        "📱 Avoid all screens for 2 hours before bed"
                    ])
                elif sleep_hours < 5:
                    risks.append(f"⚠️ Very low sleep ({sleep_hours:.1f} hours)")
                    risk_level = "high" if risk_level != "critical" else risk_level
                    recommendations.extend([
                        "😴 Aim for 7-9 hours tonight",
                        "🧘 Try relaxation yoga before bed",
                        "🛁 Take a warm bath to promote sleep"
                    ])
                elif sleep_hours < 6:
                    risks.append(f"💤 Insufficient sleep ({sleep_hours:.1f} hours)")
                    risk_level = "medium" if risk_level == "low" else risk_level
                    recommendations.extend([
                        "😴 Establish a consistent bedtime routine",
                        "📱 Limit screen time before bed"
                    ])
            
            # 3️⃣ Low HRV (if available)
            if hrv_ms is not None:
                if hrv_ms < 20:
                    risks.append(f"⚠️ Very low HRV ({hrv_ms} ms) - Burnout risk")
                    risk_level = "high" if risk_level not in ["critical"] else risk_level
                    recommendations.extend([
                        "🧘 Practice mindfulness meditation",
                        "🌳 Spend time in nature",
                        "💆 Consider restorative yoga"
                    ])
                elif hrv_ms < 30:
                    risks.append(f"📉 Low HRV ({hrv_ms} ms) - High stress")
                    risk_level = "medium" if risk_level == "low" else risk_level
                    recommendations.extend([
                        "💨 Try breathing exercises",
                        "🚶 Take gentle walks"
                    ])
            
            # 4️⃣ Abnormal Activity Levels
            if steps is not None:
                if steps < 2000:
                    risks.append(f"🪑 Very low activity ({steps} steps)")
                    risk_level = "medium" if risk_level == "low" else risk_level
                    recommendations.extend([
                        "🚶 Take short walks every hour (5-10 min)",
                        "🧘 Try gentle yoga or stretching",
                        "🎯 Aim for at least 5,000 steps daily"
                    ])
                elif steps > 15000:
                    risks.append(f"🏃 Very high activity ({steps} steps)")
                    risk_level = "medium" if risk_level == "low" else risk_level
                    recommendations.extend([
                        "🧘 Prioritize stretching and recovery",
                        "💧 Stay well hydrated",
                        "😴 Ensure adequate rest"
                    ])
            
            # 5️⃣ High Self-Reported Stress
            if stress_level:
                if stress_level >= 8:
                    risks.append(f"😰 Very high stress level ({stress_level}/10)")
                    risk_level = "high" if risk_level not in ["critical"] else risk_level
                    recommendations.extend([
                        "🧘 Practice mindfulness meditation NOW",
                        "💨 Try box breathing (4-4-4-4 pattern)",
                        "🌳 Take a break - go outside",
                        "💬 Talk to someone you trust"
                    ])
                elif stress_level >= 7:
                    risks.append(f"😓 High stress level ({stress_level}/10)")
                    risk_level = "medium" if risk_level == "low" else risk_level
                    recommendations.extend([
                        "🧘 10-minute meditation session",
                        "🚶 Short outdoor walk",
                        "💆 Progressive muscle relaxation"
                    ])
            
            # 6️⃣ COMBINED RED FLAGS
            if sleep_hours and sleep_hours < 6 and heart_rate and heart_rate >= 90:
                risks.append("🔴 BURNOUT ALERT: Low sleep + Elevated heart rate")
                risk_level = "high" if risk_level != "critical" else risk_level
                recommendations.insert(0, "⚠️ Your body shows exhaustion signs. Prioritize rest IMMEDIATELY.")
            
            if sleep_hours and sleep_hours < 6 and hrv_ms and hrv_ms < 30:
                risks.append("🔴 RECOVERY FAILURE: Poor sleep + Low HRV")
                risk_level = "high" if risk_level != "critical" else risk_level
                recommendations.insert(0, "⚠️ Your body isn't recovering. Focus on deep rest and sleep hygiene.")
            
            if (stress_level and stress_level >= 7 and 
                heart_rate and heart_rate >= 90 and 
                sleep_hours and sleep_hours < 6):
                risks.append("🚨 TRIPLE THREAT: High stress + Elevated HR + Poor sleep")
                risk_level = "critical"
                recommendations.insert(0, "🚨 CRITICAL: Multiple red flags. Take immediate action!")
            
            # Deduplicate recommendations
            recommendations = list(dict.fromkeys(recommendations))
            
            # Store device recommendations in the unified recommendation system
            try:
                if recommendations:
                    from datetime import date
                    import asyncio
                    import threading
                    
                    # Convert to date object for storage
                    target_date = date.fromisoformat(latest.get("date", date.today().isoformat()))
                    data_source = latest.get("source", "manual")  # Get source from data (manual or watch)
                    
                    logger.info(f"[DEVICE_RECS] Attempting to store {len(recommendations[:10])} device recommendations from {data_source} for {target_date}")
                    
                    # Store recommendations synchronously using threading to avoid async issues
                    def store_device_recs():
                        try:
                            from app.services.recommendation_service import recommendation_service
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(
                                recommendation_service.save_device_recommendations(
                                    user_id=user_id,
                                    target_date=target_date,
                                    device_recs=recommendations[:10],  # Top 10
                                    source_type=data_source  # Pass source (manual or watch)
                                )
                            )
                            loop.close()
                            logger.info(f"[DEVICE_RECS] ✅ Successfully stored {len(result)} device recommendations from {data_source} for user {user_id}")
                        except Exception as e:
                            logger.error(f"[DEVICE_RECS] ❌ Failed to store device recommendations: {e}", exc_info=True)
                    
                    # Run in a separate thread to avoid blocking
                    thread = threading.Thread(target=store_device_recs, daemon=True)
                    thread.start()
                        
            except Exception as rec_store_err:
                logger.warning(f"Non-critical error storing device recommendations: {rec_store_err}")
            
            return {
                "has_risks": len(risks) > 0,
                "risk_level": risk_level,
                "risks": risks,
                "recommendations": recommendations[:10],  # Top 10
                "data": latest
            }
            
        except Exception as e:
            logger.error(f"Error analyzing health risks: {e}", exc_info=True)
            return {
                "has_risks": False,
                "risk_level": "error",
                "risks": [],
                "recommendations": ["❌ Error analyzing data. Please try again."],
                "data": None
            }
