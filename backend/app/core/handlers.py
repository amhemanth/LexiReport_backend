import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import (
    LexiReportException,
    ValidationException,
    AuthenticationException,
    PermissionException,
    NotFoundException,
    AIProcessingError,
    validation_exception_handler as base_validation_handler,
    authentication_exception_handler as base_auth_handler,
    permission_exception_handler as base_permission_handler,
    not_found_exception_handler as base_not_found_handler
)

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    # Convert ValueError objects in the error context to strings
    errors = exc.errors()
    for error in errors:
        ctx = error.get('ctx')
        if ctx and 'error' in ctx and isinstance(ctx['error'], ValueError):
            ctx['error'] = str(ctx['error'])
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

async def lexireport_exception_handler(request: Request, exc: LexiReportException):
    """Handle LexiReport exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail) if isinstance(exc.detail, (ValueError, str)) else exc.detail}
    )

async def ai_processing_exception_handler(request: Request, exc: AIProcessingError):
    """Handle AI processing exceptions."""
    logger.error(f"AI processing error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc.detail) if isinstance(exc.detail, (ValueError, str)) else exc.detail,
            "error_type": "ai_processing_error",
            "error_code": exc.error_code if hasattr(exc, 'error_code') else None
        }
    )

# Export all handlers
__all__ = [
    'validation_exception_handler',
    'general_exception_handler',
    'lexireport_exception_handler',
    'ai_processing_exception_handler',
    'base_validation_handler',
    'base_auth_handler',
    'base_permission_handler',
    'base_not_found_handler',
    'http_exception_handler'
] 