# utils/email_utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
import traceback
import smtplib

# Create a logger for this module
logger = logging.getLogger(__name__)

def send_otp_email(email, otp_code, first_name=None):
    """
    Send OTP verification email
    """
    subject = 'Verify Your Email - SRI VARAM MANAMALAI '
    
    context = {
        'otp_code': otp_code,
        'first_name': first_name or 'User',
        'expiry_minutes': 10,
        'site_name': 'SRI VARAM MANAMALAI ',
    }
    
    try:
        logger.info(f"📧 Preparing email for {email}")
        logger.info(f"🔑 OTP Code: {otp_code}")
        
        # Check if email settings are configured
        if not settings.EMAIL_HOST_USER:
            logger.error("❌ EMAIL_HOST_USER is not configured")
            return False
        
        # For debugging, log the email settings (without password)
        logger.info(f"📨 Email backend: {settings.EMAIL_BACKEND}")
        logger.info(f"📨 Email host: {settings.EMAIL_HOST}")
        logger.info(f"📨 Email user: {settings.EMAIL_HOST_USER}")
        logger.info(f"📨 From email: {settings.DEFAULT_FROM_EMAIL}")
        
        # Render email template
        try:
            html_message = render_to_string('emails/otp_verification.html', context)
            plain_message = strip_tags(html_message)
            logger.info("✅ Email template rendered successfully")
        except Exception as template_error:
            logger.error(f"❌ Template rendering error: {str(template_error)}")
            # Fallback plain text
            plain_message = f"Your OTP code is: {otp_code}"
            html_message = f"<h1>Your OTP code is: {otp_code}</h1>"
        
        # Send email
        logger.info(f"📤 Sending email to {email}...")
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"✅ OTP email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication Error: {str(e)}")
        logger.error("Please check your email username and app password")
        return False
        
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP Exception: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected error sending email to {email}: {str(e)}")
        logger.error(traceback.format_exc())
        return False