"""
Wearable Health Anomaly Detection
Analyzes wearable data for health risks and triggers alerts.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.utils.database import get_supabase
from app.services.alert_service import AlertService
from app.services.notification_service import get_notification_service
from app.services.sms_service import get_sms_service

logger = logging.getLogger(__name__)


class WearableHealthAnalyzer:
    """Detects health anomalies from wearable data and creates alerts."""
    
    # Thresholds for anomaly detection
    VERY_HIGH_RHR_THRESHOLD = 90  # bpm at rest - stress/anxiety indicator
    HIGH_HEART_RATE_THRESHOLD = 100  # bpm for extended period
    EXTREME_HEART_RATE_THRESHOLD = 120  # bpm - critical
    
    LOW_SLEEP_THRESHOLD = 6.0  # hours - insufficient
    VERY_LOW_SLEEP_THRESHOLD = 5.0  # hours - severe sleep deprivation
    CRITICAL_SLEEP_THRESHOLD = 4.0  # hours - critical
    
    LOW_HRV_THRESHOLD = 30  # ms - poor recovery
    VERY_LOW_HRV_THRESHOLD = 20  # ms - high stress/burnout risk
    
    LOW_STEPS_THRESHOLD = 2000  # sedentary behavior
    HIGH_STEPS_THRESHOLD = 15000  # possible overtraining
    
    HIGH_STRESS_THRESHOLD = 7  # 1-10 scale - emotional strain
    VERY_HIGH_STRESS_THRESHOLD = 8  # 1-10 scale - severe stress
    
    @staticmethod
    async def analyze_and_alert(user_id: str, snapshot_data: Dict) -> Optional[Dict]:
        """
        Analyze wearable snapshot for anomalies and create alerts if needed.
        
        Checks for:
        1. Very high resting heart rate (>90 bpm)
        2. Low sleep duration (<6 hours) or poor quality
        3. Low HRV (heart rate variability)
        4. Abnormal activity levels (very low or very high steps)
        5. High self-reported stress (>7)
        6. Combined red flags (sleep + HR + HRV mismatches)
        
        Args:
            user_id: User ID
            snapshot_data: Wearable snapshot data
            
        Returns:
            Alert data if created, None otherwise
        """
        try:
            supabase = get_supabase()
            anomalies = []
            severity = "low"
            recommendations = []
            
            # Extract metrics
            heart_rate = snapshot_data.get("heart_rate")
            sleep_hours = snapshot_data.get("sleep_hours")
            hrv_ms = snapshot_data.get("hrv_ms")
            steps = snapshot_data.get("steps")
            stress_level = snapshot_data.get("stress_level")
            
            # 1️⃣ Check for Very High Resting Heart Rate (>90 bpm)
            if heart_rate:
                if heart_rate >= WearableHealthAnalyzer.EXTREME_HEART_RATE_THRESHOLD:
                    anomalies.append(f"critically high heart rate ({heart_rate} bpm)")
                    severity = "critical"
                    recommendations.extend([
                        "🚨 Stop any strenuous activity immediately",
                        "💨 Practice deep breathing for 5-10 minutes",
                        "🏥 If symptoms persist, seek medical attention"
                    ])
                elif heart_rate >= WearableHealthAnalyzer.HIGH_HEART_RATE_THRESHOLD:
                    anomalies.append(f"very high heart rate ({heart_rate} bpm)")
                    severity = "high" if severity not in ["critical"] else severity
                    recommendations.extend([
                        "💨 Try 10 minutes of deep breathing exercises",
                        "☕ Avoid caffeine and stimulants",
                        "🧘 Practice relaxation techniques (yoga, meditation)"
                    ])
                elif heart_rate >= WearableHealthAnalyzer.VERY_HIGH_RHR_THRESHOLD:
                    anomalies.append(f"elevated resting heart rate ({heart_rate} bpm)")
                    severity = "medium" if severity == "low" else severity
                    recommendations.extend([
                        "💧 Stay hydrated - drink water regularly",
                        "💨 Practice breathing exercises (4-7-8 technique)",
                        "😴 Ensure adequate sleep tonight (7-9 hours)",
                        "🧘 Try gentle yoga or stretching"
                    ])
            
            # 2️⃣ Check for Low Sleep Duration / Poor Sleep Quality
            if sleep_hours is not None:
                if sleep_hours < WearableHealthAnalyzer.CRITICAL_SLEEP_THRESHOLD:
                    anomalies.append(f"critical sleep deprivation ({sleep_hours:.1f} hours)")
                    severity = "critical" if severity != "critical" else severity
                    recommendations.extend([
                        "🚨 Prioritize sleep immediately - aim for 8+ hours tonight",
                        "😴 Take a 20-30 minute power nap if possible",
                        "📱 Avoid all screens 2 hours before bed",
                        "🧘 Practice Yoga Nidra (yogic sleep) for deep rest"
                    ])
                elif sleep_hours < WearableHealthAnalyzer.VERY_LOW_SLEEP_THRESHOLD:
                    anomalies.append(f"severe sleep deficiency ({sleep_hours:.1f} hours)")
                    severity = "high" if severity not in ["critical"] else severity
                    recommendations.extend([
                        "😴 Aim for 7-9 hours of sleep tonight",
                        "📱 Avoid screens 1 hour before bed",
                        "🛁 Take a warm bath or shower before sleep",
                        "🧘 Try relaxation yoga poses (Child's Pose, Legs-Up-Wall)"
                    ])
                elif sleep_hours < WearableHealthAnalyzer.LOW_SLEEP_THRESHOLD:
                    anomalies.append(f"insufficient sleep ({sleep_hours:.1f} hours)")
                    severity = "medium" if severity == "low" else severity
                    recommendations.extend([
                        "😴 Aim for 7-9 hours of sleep consistently",
                        "⏰ Establish a regular bedtime routine",
                        "🧘 Practice sleep hygiene (cool room, dark, quiet)"
                    ])
            
            # 3️⃣ Check for Low HRV (Heart Rate Variability)
            if hrv_ms is not None:
                if hrv_ms < WearableHealthAnalyzer.VERY_LOW_HRV_THRESHOLD:
                    anomalies.append(f"very low HRV ({hrv_ms} ms) - burnout risk")
                    severity = "high" if severity not in ["critical"] else severity
                    recommendations.extend([
                        "🧘 Practice mindfulness meditation for 15-20 minutes",
                        "🌳 Spend time in nature for stress recovery",
                        "😴 Prioritize quality sleep and rest days",
                        "💆 Consider gentle restorative yoga"
                    ])
                elif hrv_ms < WearableHealthAnalyzer.LOW_HRV_THRESHOLD:
                    anomalies.append(f"low HRV ({hrv_ms} ms) - high stress indicator")
                    severity = "medium" if severity == "low" else severity
                    recommendations.extend([
                        "🧘 Try 10 minutes of breathing exercises",
                        "🚶 Take a gentle walk to reset your nervous system",
                        "💆 Practice relaxation techniques"
                    ])
            
            # 4️⃣ Check for Abnormal Activity Levels (Steps)
            if steps is not None:
                if steps < WearableHealthAnalyzer.LOW_STEPS_THRESHOLD:
                    anomalies.append(f"very low activity ({steps} steps)")
                    severity = "medium" if severity == "low" else severity
                    recommendations.extend([
                        "🚶 Take short walks every hour (5-10 minutes)",
                        "🧘 Try gentle yoga or stretching",
                        "🏃 Aim for at least 5,000 steps daily"
                    ])
                elif steps > WearableHealthAnalyzer.HIGH_STEPS_THRESHOLD:
                    anomalies.append(f"very high activity ({steps} steps)")
                    severity = "medium" if severity == "low" else severity
                    recommendations.extend([
                        "🧘 Prioritize stretching and recovery",
                        "💧 Stay well hydrated",
                        "😴 Ensure adequate rest and sleep"
                    ])
            
            # 5️⃣ Check for High Self-Reported Stress
            if stress_level:
                if stress_level >= WearableHealthAnalyzer.VERY_HIGH_STRESS_THRESHOLD:
                    anomalies.append(f"very high stress level ({stress_level}/10)")
                    severity = "high" if severity not in ["critical"] else severity
                    recommendations.extend([
                        "🧘 Practice mindfulness meditation immediately",
                        "💨 Try box breathing (4-4-4-4 pattern)",
                        "🌳 Take a break - go outside for fresh air",
                        "💬 Consider talking to someone you trust"
                    ])
                elif stress_level >= WearableHealthAnalyzer.HIGH_STRESS_THRESHOLD:
                    anomalies.append(f"high stress level ({stress_level}/10)")
                    severity = "medium" if severity == "low" else severity
                    recommendations.extend([
                        "🧘 Practice mindfulness meditation for 10 minutes",
                        "🚶 Take a short walk outdoors",
                        "💆 Try progressive muscle relaxation"
                    ])
            
            # 6️⃣ Check for COMBINED RED FLAGS (Critical Combinations)
            combined_flags = []
            
            # Low sleep + High HR = Burnout risk
            if (sleep_hours and sleep_hours < WearableHealthAnalyzer.LOW_SLEEP_THRESHOLD and 
                heart_rate and heart_rate >= WearableHealthAnalyzer.VERY_HIGH_RHR_THRESHOLD):
                combined_flags.append("sleep deprivation + elevated heart rate = burnout risk")
                severity = "high" if severity not in ["critical"] else severity
                recommendations.insert(0, "⚠️ BURNOUT ALERT: Your body shows signs of exhaustion. Prioritize rest immediately.")
            
            # Low sleep + Low HRV = Recovery failure
            if (sleep_hours and sleep_hours < WearableHealthAnalyzer.LOW_SLEEP_THRESHOLD and 
                hrv_ms and hrv_ms < WearableHealthAnalyzer.LOW_HRV_THRESHOLD):
                combined_flags.append("poor sleep + low HRV = body recovery failure")
                severity = "high" if severity not in ["critical"] else severity
                recommendations.insert(0, "⚠️ RECOVERY ALERT: Your body isn't recovering properly. Focus on deep rest and sleep hygiene.")
            
            # High stress + High HR + Low sleep = Triple threat
            if (stress_level and stress_level >= WearableHealthAnalyzer.HIGH_STRESS_THRESHOLD and
                heart_rate and heart_rate >= WearableHealthAnalyzer.VERY_HIGH_RHR_THRESHOLD and
                sleep_hours and sleep_hours < WearableHealthAnalyzer.LOW_SLEEP_THRESHOLD):
                combined_flags.append("high stress + elevated HR + poor sleep = severe strain")
                severity = "critical"
                recommendations.insert(0, "🚨 CRITICAL: Multiple health red flags detected. Take immediate action to reduce stress and prioritize sleep.")
            
            # Add combined flags to anomalies
            if combined_flags:
                anomalies.extend(combined_flags)
            
            # If anomalies detected, create alert
            if anomalies:
                alert_data = await WearableHealthAnalyzer._create_wearable_alert(
                    supabase=supabase,
                    user_id=user_id,
                    anomalies=anomalies,
                    severity=severity,
                    recommendations=recommendations,
                    snapshot_data=snapshot_data
                )
                return alert_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing wearable data for alerts: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def _create_wearable_alert(
        supabase,
        user_id: str,
        anomalies: List[str],
        severity: str,
        recommendations: List[str],
        snapshot_data: Dict
    ) -> Dict:
        """
        Create a wearable health alert with in-app notification and conditional SMS.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            anomalies: List of detected anomalies
            severity: Alert severity
            recommendations: List of actionable recommendations
            snapshot_data: Original snapshot data
            
        Returns:
            Created alert data
        """
        try:
            # Get user profile for phone number
            profile_result = supabase.table("profiles").select(
                "id, email, phone_number"
            ).eq("id", user_id).single().execute()
            
            profile = profile_result.data if profile_result.data else {}
            phone_number = profile.get("phone_number")
            
            # Create alert title and message
            anomaly_text = ", ".join(anomalies)
            title = f"Health Alert: {anomaly_text.capitalize()}"
            
            # Get top recommendations for concise message
            top_recommendations = recommendations[:3]
            rec_text = " ".join(f"{i+1}. {rec}" for i, rec in enumerate(top_recommendations))
            
            message = f"We detected {anomaly_text}. Recommendations: {rec_text}"
            
            # Create alert record in database using AlertService
            alert_result = await AlertService.create_wearable_alert(
                supabase=supabase,
                user_id=user_id,
                severity=severity,
                title=title,
                message=message,
                anomalies=anomalies,
                snapshot_data=snapshot_data
            )
            
            # 1. ALWAYS create in-app notification
            notification_service = get_notification_service()
            risk_level = "high" if severity in ["high", "critical"] else "medium" if severity == "medium" else "low"
            
            notification = await notification_service.create_health_alert_notification(
                user_id=user_id,
                concerns=anomalies,
                recommendations=recommendations,
                risk_level=risk_level
            )
            
            if notification:
                logger.info(f"✅ Created in-app notification for user {user_id}")
            else:
                logger.warning(f"⚠️ Failed to create in-app notification for user {user_id}")
            
            # 2. Send SMS if phone number exists
            if phone_number:
                try:
                    sms_service = get_sms_service()
                    
                    # Send SMS with concerns and recommendations
                    sms_sent = await sms_service.send_health_alert(
                        to_number=phone_number,
                        concerns=anomalies[:3],  # Limit to 3 for SMS length
                        recommendations=recommendations[:3]
                    )
                    
                    if sms_sent:
                        logger.info(f"✅ SMS alert sent to user {user_id} at {phone_number}")
                        
                        # Update alert to reflect SMS was sent
                        supabase.table("alerts").update({
                            "notified_via_sms": True,
                            "sms_sent_at": datetime.now().isoformat()
                        }).eq("id", alert_result["id"]).execute()
                    else:
                        logger.warning(f"⚠️ SMS failed for user {user_id}")
                    
                except Exception as sms_error:
                    logger.error(f"❌ Failed to send SMS alert: {sms_error}")
                    # Don't fail the whole process if SMS fails
            else:
                logger.info(f"ℹ️ No phone number for user {user_id}, skipping SMS")
                
                # Create a gentle reminder notification to add phone number
                await notification_service.create_notification(
                    user_id=user_id,
                    notification_type="system",
                    title="📱 Add Phone Number for SMS Alerts",
                    message="Enable SMS health alerts by adding your phone number in Account Settings.",
                    data={"action_url": "/account-settings"}
                )
            
            return alert_result
            
        except Exception as e:
            logger.error(f"❌ Error creating wearable alert: {e}")
            raise


    @staticmethod
    async def analyze_daily_trends(user_id: str) -> Optional[Dict]:
        """
        Analyze trends over the past few days to detect patterns.
        This can be called periodically (e.g., daily background job).
        
        Args:
            user_id: User ID
            
        Returns:
            Trend analysis results or None
        """
        try:
            supabase = get_supabase()
            
            # Get last 7 days of daily stats
            lookback_date = (datetime.now() - timedelta(days=7)).date()
            
            stats_result = supabase.table("wearable_daily_stats").select(
                "*"
            ).eq("user_id", user_id).gte(
                "date", lookback_date.isoformat()
            ).order("date", desc=False).execute()
            
            if not stats_result.data or len(stats_result.data) < 3:
                logger.info(f"Insufficient data for trend analysis for user {user_id}")
                return None
            
            stats = stats_result.data
            
            # Analyze trends
            avg_sleep = sum(s["sleep_hours"] for s in stats if s.get("sleep_hours")) / len([s for s in stats if s.get("sleep_hours")])
            avg_heart_rate = sum(s["avg_heart_rate"] for s in stats if s.get("avg_heart_rate")) / len([s for s in stats if s.get("avg_heart_rate")])
            avg_stress = sum(s["avg_stress_level"] for s in stats if s.get("avg_stress_level")) / len([s for s in stats if s.get("avg_stress_level")])
            
            trends = {
                "avg_sleep_past_week": round(avg_sleep, 2),
                "avg_heart_rate_past_week": round(avg_heart_rate, 2),
                "avg_stress_past_week": round(avg_stress, 2),
                "needs_attention": []
            }
            
            if avg_sleep < 6.0:
                trends["needs_attention"].append("Consistently low sleep")
            if avg_heart_rate > 85:
                trends["needs_attention"].append("Elevated resting heart rate")
            if avg_stress > 6:
                trends["needs_attention"].append("High stress levels")
            
            logger.info(f"Trend analysis for user {user_id}: {trends}")
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing daily trends: {e}")
            return None
