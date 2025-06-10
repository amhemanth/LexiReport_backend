from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

class LexiReportException(HTTPException):
    """Base exception for LexiReport."""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class ValidationException(LexiReportException):
    """Validation exception."""
    def __init__(self, detail: Any = None):
        if isinstance(detail, dict):
            formatted_detail = {
                "message": "Validation error",
                "errors": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            formatted_detail = {
                "message": str(detail),
                "timestamp": datetime.utcnow().isoformat()
            }
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=formatted_detail
        )

class AuthenticationException(LexiReportException):
    """Authentication exception."""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

class PermissionException(LexiReportException):
    """Permission exception."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class NotFoundException(LexiReportException):
    """Not found exception."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class SecurityException(LexiReportException):
    """Security-related exception."""
    def __init__(self, detail: str = "Security violation"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class RateLimitExceededError(LexiReportException):
    """Rate limit exceeded exception."""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat(),
                "retry_after": 60
            },
            headers={"Retry-After": "60"}
        )

class AccountLockedError(AuthenticationException):
    """Account locked due to too many failed attempts."""
    def __init__(self, lockout_time: int):
        super().__init__(
            detail={
                "message": f"Account is locked. Please try again in {lockout_time} minutes",
                "timestamp": datetime.utcnow().isoformat(),
                "lockout_time": lockout_time
            }
        )

class InvalidTokenError(AuthenticationException):
    """Invalid or expired token error."""
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail=detail)

class TokenRevokedError(AuthenticationException):
    """Token has been revoked error."""
    def __init__(self):
        super().__init__(detail="Token has been revoked")

class PasswordHistoryError(ValidationException):
    """Password was used before error."""
    def __init__(self):
        super().__init__(
            detail={
                "message": "Password was used before. Please choose a different password",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class PasswordStrengthError(ValidationException):
    """Password strength validation error."""
    def __init__(self, detail: str):
        super().__init__(
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

def authentication_exception_handler(request: Request, exc: AuthenticationException) -> JSONResponse:
    """Handle authentication exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
        headers=exc.headers
    )

def permission_exception_handler(request: Request, exc: PermissionException) -> JSONResponse:
    """Handle permission exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    """Handle not found exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

class DatabaseError(HTTPException):
    """Database operation error."""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class UserNotFoundError(HTTPException):
    """User not found error."""
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class UserAlreadyExistsError(HTTPException):
    """User already exists error."""
    def __init__(self, detail: str = "User already exists"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class AuthenticationError(HTTPException):
    """Authentication error."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

class InvalidCredentialsError(HTTPException):
    """Invalid credentials error."""
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

class InactiveUserError(HTTPException):
    """Inactive user error."""
    def __init__(self, detail: str = "Inactive user"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class AIProcessingError(HTTPException):
    """AI processing error."""
    def __init__(self, detail: str = "AI processing failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

def ai_processing_exception_handler(request: Request, exc: AIProcessingError) -> JSONResponse:
    """Handle AI processing exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

class PermissionDeniedError(HTTPException):
    """Permission denied error."""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        ) 