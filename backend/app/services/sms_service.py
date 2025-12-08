"""
SMS Service - Handles SMS notifications via Twilio
"""

import logging
import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)

class SMSService:
    """Service for sending SMS notifications via Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if self.account_sid and self.auth_token and self.from_number:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
            logger.info("✅ Twilio SMS Service initialized successfully")
        else:
            self.client = None
            self.enabled = False
            logger.warning("⚠️ Twilio credentials not found. SMS service disabled.")
            logger.warning("Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env")
    
    async def send_health_alert(
        self, 
        to_number: str, 
        concerns: list[str], 
        recommendations: list[str]
    ) -> bool:
        """
        Send health alert SMS with detected concerns and recommendations
        
        Args:
            to_number: User's phone number (with country code, e.g., +1234567890)
            concerns: List of detected health concerns
            recommendations: List of recommended actions
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("SMS service not enabled. Skipping SMS.")
            return False
        
        if not to_number:
            logger.warning("No phone number provided. Skipping SMS.")
            return False
        
        try:
            # Format the message
            message_parts = ["🏥 Nirvami Health Alert\n"]
            
            if concerns:
                message_parts.append("\n⚠️ Detected Concerns:")
                for i, concern in enumerate(concerns[:3], 1):  # Limit to 3 concerns for SMS length
                    message_parts.append(f"{i}. {concern}")
            
            if recommendations:
                message_parts.append("\n\n✅ Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):  # Limit to 3 recommendations
                    message_parts.append(f"{i}. {rec}")
            
            message_parts.append("\n\nOpen the Nirvami app for full details.")
            
            message_body = "\n".join(message_parts)
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"✅ SMS sent successfully to {to_number}. SID: {message.sid}")
            return True
            
        except TwilioRestException as e:
            logger.error(f"❌ Twilio error sending SMS to {to_number}: {e.msg}")
            logger.error(f"Error code: {e.code}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending SMS to {to_number}: {str(e)}")
            return False
    
    async def send_custom_sms(self, to_number: str, message: str) -> bool:
        """
        Send a custom SMS message
        
        Args:
            to_number: User's phone number (with country code)
            message: Message text
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("SMS service not enabled. Skipping SMS.")
            return False
        
        if not to_number:
            logger.warning("No phone number provided. Skipping SMS.")
            return False
        
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"✅ Custom SMS sent to {to_number}. SID: {msg.sid}")
            return True
            
        except TwilioRestException as e:
            logger.error(f"❌ Twilio error: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending SMS: {str(e)}")
            return False


# Singleton instance
_sms_service = None

def get_sms_service() -> SMSService:
    """Get the singleton SMS service instance"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service
