"""Email sending functionality."""
from typing import Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from app.config.settings import get_settings
from app.core.logger import logger

settings = get_settings()

def get_email_template(template_name: str) -> str:
    """Get email template content."""
    try:
        template_dir = Path(settings.EMAIL_TEMPLATES_DIR)
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(f"{template_name}.html")
        return template
    except Exception as e:
        logger.error(f"Failed to load email template {template_name}: {str(e)}")
        return None

def send_email(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any],
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
) -> bool:
    """
    Send an email using the specified template.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        template_name: Name of the template file (without .html extension)
        template_data: Data to be used in the template
        from_email: Sender email address (defaults to settings.EMAILS_FROM_EMAIL)
        from_name: Sender name (defaults to settings.EMAILS_FROM_NAME)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not settings.EMAILS_ENABLED:
        logger.warning("Email sending is disabled")
        return False

    try:
        # Get template
        template = get_email_template(template_name)
        if not template:
            return False

        # Prepare email
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = f"{from_name or settings.EMAILS_FROM_NAME} <{from_email or settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to

        # Render template
        html_content = template.render(**template_data)
        msg.attach(MIMEText(html_content, "html"))

        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {email_to}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {str(e)}")
        return False

def send_verification_email(email_to: str, token: str) -> bool:
    """
    Send email verification email.
    
    Args:
        email_to: Recipient email address
        token: Verification token
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    verification_url = f"{settings.SERVER_HOST}/verify-email?token={token}"
    return send_email(
        email_to=email_to,
        subject="Verify your email address",
        template_name="email_verification",
        template_data={
            "verification_url": verification_url,
            "expiry_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
        }
    )

def send_password_reset_email(email_to: str, token: str) -> bool:
    """
    Send password reset email.
    
    Args:
        email_to: Recipient email address
        token: Password reset token
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    reset_url = f"{settings.SERVER_HOST}/reset-password?token={token}"
    return send_email(
        email_to=email_to,
        subject="Reset your password",
        template_name="password_reset",
        template_data={
            "reset_url": reset_url,
            "expiry_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
        }
    )

def send_welcome_email(email_to: str, full_name: str) -> bool:
    """
    Send welcome email to new users.
    
    Args:
        email_to: Recipient email address
        full_name: User's full name
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    return send_email(
        email_to=email_to,
        subject="Welcome to LexiReport",
        template_name="welcome",
        template_data={
            "full_name": full_name,
            "login_url": f"{settings.SERVER_HOST}/login"
        }
    )

def send_account_locked_email(email_to: str, lockout_time: int) -> bool:
    """
    Send account locked notification email.
    
    Args:
        email_to: Recipient email address
        lockout_time: Lockout duration in minutes
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    return send_email(
        email_to=email_to,
        subject="Account Locked",
        template_name="account_locked",
        template_data={
            "lockout_time": lockout_time,
            "support_email": settings.EMAILS_FROM_EMAIL
        }
    ) 