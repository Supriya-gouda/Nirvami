"""Email utility for sending confirmation emails."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_confirmation_email(to_email: str, confirmation_url: str, full_name: Optional[str] = None) -> bool:
    """
    Send email confirmation using SMTP.
    
    Args:
        to_email: Recipient email address
        confirmation_url: URL for email confirmation
        full_name: User's full name (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", "noreply@nirvami.app")
    
    # Check if SMTP is configured
    if not smtp_user or not smtp_password or smtp_user == "your-email@gmail.com":
        logger.warning("SMTP not configured. Skipping email send.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Confirm your Nirvami account"
        msg["From"] = from_email
        msg["To"] = to_email
        
        # Create HTML email
        greeting = f"Hi {full_name}," if full_name else "Hi,"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: white; margin: 0;">Welcome to Nirvami</h1>
                    </div>
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">{greeting}</p>
                        <p style="font-size: 16px;">Thank you for signing up! Please confirm your email address to activate your account.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{confirmation_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block;">
                                Confirm Email
                            </a>
                        </div>
                        <p style="font-size: 14px; color: #666;">Or copy and paste this link in your browser:</p>
                        <p style="font-size: 14px; word-break: break-all; background: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                            {confirmation_url}
                        </p>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        <p style="font-size: 12px; color: #999; text-align: center;">
                            If you didn't create an account with Nirvami, you can safely ignore this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        text = f"""
        {greeting}
        
        Thank you for signing up for Nirvami!
        
        Please confirm your email address by clicking the link below:
        {confirmation_url}
        
        If you didn't create an account with Nirvami, you can safely ignore this email.
        """
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        logger.info(f"Connecting to SMTP server {smtp_host}:{smtp_port}")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Confirmation email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email to {to_email}: {e}")
        return False


def send_welcome_email(to_email: str, full_name: Optional[str] = None) -> bool:
    """
    Send welcome email after successful confirmation.
    
    Args:
        to_email: Recipient email address
        full_name: User's full name (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", "noreply@nirvami.app")
    
    # Check if SMTP is configured
    if not smtp_user or not smtp_password or smtp_user == "your-email@gmail.com":
        logger.warning("SMTP not configured. Skipping email send.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Welcome to Nirvami - Your Mental Wellness Journey Begins"
        msg["From"] = from_email
        msg["To"] = to_email
        
        greeting = f"Hi {full_name}," if full_name else "Hi,"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: white; margin: 0;">🎉 Welcome to Nirvami!</h1>
                    </div>
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">{greeting}</p>
                        <p style="font-size: 16px;">Your account is now active! We're excited to support you on your mental wellness journey.</p>
                        <h3 style="color: #667eea;">What's next?</h3>
                        <ul style="font-size: 15px; line-height: 2;">
                            <li>Log your daily mood and emotions</li>
                            <li>Chat with our AI wellness companion</li>
                            <li>Explore yoga and lifestyle tips</li>
                            <li>Try sound therapy for relaxation</li>
                            <li>Track your progress with analytics</li>
                        </ul>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:3000/login" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block;">
                                Get Started
                            </a>
                        </div>
                        <p style="font-size: 14px; color: #666; text-align: center; margin-top: 30px;">
                            Need help? Reply to this email or contact our support team.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        text = f"""
        {greeting}
        
        Your account is now active! We're excited to support you on your mental wellness journey.
        
        What's next?
        - Log your daily mood and emotions
        - Chat with our AI wellness companion
        - Explore yoga and lifestyle tips
        - Try sound therapy for relaxation
        - Track your progress with analytics
        
        Get started: http://localhost:3000/login
        
        Need help? Reply to this email or contact our support team.
        """
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Welcome email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        return False
