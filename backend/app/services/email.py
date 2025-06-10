from typing import Optional
from fastapi import HTTPException
from app.core.email import (
    send_email,
    send_verification_email,
    send_password_reset_email,
    send_welcome_email,
    send_account_locked_email
)
from app.config.settings import get_settings
from app.core.logger import logger, log_error, log_warning

settings = get_settings()

class EmailService:
    def __init__(self):
        self.enabled = bool(
            settings.SMTP_HOST and
            settings.SMTP_PORT and
            settings.SMTP_USER and
            settings.SMTP_PASSWORD
        )
        if not self.enabled:
            log_warning(logger, "Email service is disabled - SMTP settings not configured")

    async def send_verification(self, email: str, token: str) -> bool:
        """Send email verification link"""
        if not self.enabled:
            log_warning(logger, "Email verification skipped - email service disabled")
            return False
            
        try:
            verification_url = f"/verify-email?token={token}"
            await send_verification_email(
                email_to=email,
                verification_url=verification_url,
                expiry_hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
            )
            return True
        except Exception as e:
            log_error(logger, e, {"email": email})
            return False

    async def send_password_reset(self, email: str, token: str) -> bool:
        """Send password reset link"""
        if not self.enabled:
            log_warning(logger, "Password reset email skipped - email service disabled")
            return False
            
        try:
            reset_url = f"/reset-password?token={token}"
            await send_password_reset_email(
                email_to=email,
                reset_url=reset_url,
                expiry_hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            )
            return True
        except Exception as e:
            log_error(logger, e, {"email": email})
            return False

    async def send_welcome(self, email: str, full_name: str) -> bool:
        """Send welcome email"""
        if not self.enabled:
            log_warning(logger, "Welcome email skipped - email service disabled")
            return False
            
        try:
            login_url = "/login"
            await send_welcome_email(
                email_to=email,
                full_name=full_name,
                login_url=login_url
            )
            return True
        except Exception as e:
            log_error(logger, e, {"email": email, "full_name": full_name})
            return False

    async def send_account_locked(self, email: str, token: str) -> bool:
        """Send account locked notification"""
        if not self.enabled:
            log_warning(logger, "Account locked email skipped - email service disabled")
            return False
            
        try:
            unlock_url = f"/unlock-account?token={token}"
            await send_account_locked_email(
                email_to=email,
                unlock_url=unlock_url
            )
            return True
        except Exception as e:
            log_error(logger, e, {"email": email})
            return False

# Create singleton instance
email_service = EmailService() 