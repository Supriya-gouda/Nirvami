"""Alert and notification service."""
from app.config import settings
from twilio.rest import Client as TwilioClient
from typing import List
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertService:
    """Service for creating and managing alerts and notifications."""
    
    @staticmethod
    async def create_crisis_alert(
        supabase,
        user_id: str,
        severity: str,
        triggers: List[str],
        message_content: str
    ):
        """
        Create a crisis alert and send notifications.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            severity: Alert severity
            triggers: List of trigger reasons
            message_content: Original message content
        """
        try:
            # Get user preferences
            prefs = supabase.table("user_preferences").select("*").eq("user_id", user_id).single().execute()
            preferences = prefs.data if prefs.data else {}
            
            # Get user profile for contact info
            profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
            user_profile = profile.data if profile.data else {}
            
            # Create alert record
            alert_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "alert_type": "crisis",
                "severity": severity,
                "title": "Crisis Alert Detected",
                "message": f"Crisis indicators detected: {', '.join(triggers)}",
                "triggered_by": "chat_message",
                "trigger_metadata": {
                    "triggers": triggers,
                    "message_preview": message_content[:100]
                },
                "status": "active",
                "notified_channels": [],
                "created_at": datetime.now().isoformat()
            }
            
            # Insert alert
            alert_result = supabase.table("alerts").insert(alert_data).execute()
            alert_id = alert_result.data[0]["id"]
            
            # Send notifications based on user preferences
            notified_channels = []
            
            # In-app notification (always send)
            await AlertService.create_in_app_notification(
                supabase,
                user_id,
                "Crisis Support Available",
                "We're here to help. Please consider reaching out to a crisis helpline.",
                "warning"
            )
            notified_channels.append("in_app")
            
            # Email notification
            if preferences.get("notification_email") and user_profile.get("email"):
                try:
                    await AlertService.send_email_alert(
                        user_profile["email"],
                        "Crisis Support Resources",
                        AlertService.get_crisis_email_body()
                    )
                    notified_channels.append("email")
                except Exception as e:
                    logger.error(f"Error sending email alert: {e}")
            
            # SMS notification (if enabled and Twilio configured)
            if (preferences.get("notification_sms") and 
                settings.TWILIO_ACCOUNT_SID and 
                settings.TWILIO_AUTH_TOKEN):
                try:
                    # Note: Would need phone number in profile
                    # await AlertService.send_sms_alert(phone_number, message)
                    logger.info("SMS alert would be sent (phone number needed)")
                except Exception as e:
                    logger.error(f"Error sending SMS alert: {e}")
            
            # Update alert with notified channels
            supabase.table("alerts").update({
                "notified_channels": notified_channels
            }).eq("id", alert_id).execute()
            
            logger.info(f"Crisis alert created for user {user_id}, channels: {notified_channels}")
            
        except Exception as e:
            logger.error(f"Error creating crisis alert: {e}")
            # Don't fail the whole request if alert creation fails
    
    @staticmethod
    async def create_in_app_notification(
        supabase,
        user_id: str,
        title: str,
        body: str,
        notification_type: str = "info",
        action_url: str = None
    ):
        """Create an in-app notification."""
        try:
            notification_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": title,
                "body": body,
                "type": notification_type,
                "read": False,
                "action_url": action_url,
                "created_at": datetime.now().isoformat()
            }
            
            supabase.table("notifications").insert(notification_data).execute()
            
            # TODO: Trigger Supabase Realtime broadcast
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
    
    @staticmethod
    async def send_email_alert(to_email: str, subject: str, body: str):
        """Send email alert using SMTP."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = settings.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
    
    @staticmethod
    async def send_sms_alert(to_phone: str, message: str):
        """Send SMS alert using Twilio."""
        try:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # Use Messaging Service SID if available, otherwise use phone number
            if settings.TWILIO_MESSAGING_SERVICE_SID:
                sms = client.messages.create(
                    body=message,
                    messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
                    to=to_phone
                )
            else:
                sms = client.messages.create(
                    body=message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=to_phone
                )
            
            logger.info(f"SMS sent to {to_phone}: {sms.sid}")
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise
    
    @staticmethod
    async def create_wearable_alert(
        supabase,
        user_id: str,
        severity: str,
        title: str,
        message: str,
        anomalies: list,
        snapshot_data: dict
    ):
        """
        Create a wearable health alert.
        
        Args:
            supabase: Supabase client
            user_id: User ID
            severity: Alert severity (low, medium, high, critical)
            title: Alert title
            message: Alert message
            anomalies: List of detected anomalies
            snapshot_data: Original wearable snapshot data
        
        Returns:
            Created alert record
        """
        try:
            alert_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "alert_type": "wellness_low",  # Using wellness_low for health alerts
                "severity": severity,
                "title": title,
                "message": message,
                "triggered_by": "wearable",
                "trigger_metadata": {
                    "anomalies": anomalies,
                    "snapshot_preview": {
                        "heart_rate": snapshot_data.get("heart_rate"),
                        "sleep_hours": snapshot_data.get("sleep_hours"),
                        "stress_level": snapshot_data.get("stress_level"),
                        "captured_at": snapshot_data.get("captured_at")
                    }
                },
                "status": "active",
                "notified_channels": ["in_app"],  # Will be updated if SMS sent
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase.table("alerts").insert(alert_data).execute()
            
            if result.data:
                logger.info(f"Created wearable alert for user {user_id}: {title}")
                return result.data[0]
            else:
                raise Exception("Failed to insert alert")
                
        except Exception as e:
            logger.error(f"Error creating wearable alert: {e}")
            raise
    
    @staticmethod
    def get_crisis_email_body() -> str:
        """Get HTML body for crisis alert email."""
        return """
        <html>
        <body>
            <h2>Crisis Support Resources</h2>
            <p>We noticed you may be experiencing distress. Please know that help is available 24/7.</p>
            
            <h3>Immediate Support:</h3>
            <ul>
                <li><strong>National Suicide Prevention Lifeline:</strong> 988 (US)</li>
                <li><strong>Crisis Text Line:</strong> Text HOME to 741741</li>
                <li><strong>International:</strong> <a href="https://findahelpline.com">findahelpline.com</a></li>
            </ul>
            
            <p>You are not alone. Please reach out to these resources or a trusted friend or family member.</p>
            
            <p>With care,<br>The Nirvami Team</p>
        </body>
        </html>
        """
