import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import (
    LexiReportException,
    ValidationException,
    AuthenticationException,
    PermissionException,
    NotFoundException,
    validation_exception_handler as base_validation_handler,
    authentication_exception_handler as base_auth_handler,
    permission_exception_handler as base_permission_handler,
    not_found_exception_handler as base_not_found_handler
)

logger = logging.getLogger(__name__)

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

# Export all handlers
__all__ = [
    'validation_exception_handler',
    'general_exception_handler',
    'lexireport_exception_handler',
    'base_validation_handler',
    'base_auth_handler',
    'base_permission_handler',
    'base_not_found_handler'
] 