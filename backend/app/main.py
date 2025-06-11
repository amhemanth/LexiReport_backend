import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from app.api.v1.api import api_router
from app.config.settings import get_settings
from app.core.deps import get_db
from app.core.handlers import (
    validation_exception_handler,
    general_exception_handler,
    lexireport_exception_handler,
    ai_processing_exception_handler,
    base_validation_handler,
    base_auth_handler,
    base_permission_handler,
    base_not_found_handler,
    http_exception_handler
)
from app.core.middleware import setup_middleware
from app.core.exceptions import (
    LexiReportException,
    ValidationException,
    AuthenticationException,
    PermissionException,
    NotFoundException,
    AIProcessingError,
    RateLimitExceededError,
    SecurityException
)
from app.core.model_cache import precache_models
from sqlalchemy.exc import DatabaseError
from app.core.logger import (
    logger,
    api_logger,
    error_logger,
    db_logger,
    security_logger
)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# Pre-cache models at server startup
logger.info("Starting model pre-caching...")
precache_models()

# Set up middleware
setup_middleware(app)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(LexiReportException, lexireport_exception_handler)
app.add_exception_handler(AIProcessingError, ai_processing_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AuthenticationException, base_auth_handler)
app.add_exception_handler(PermissionException, base_permission_handler)
app.add_exception_handler(NotFoundException, base_not_found_handler)
app.add_exception_handler(DatabaseError, general_exception_handler)

@app.exception_handler(RequestValidationError)
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
        content={
            "detail": errors,
            "error_type": "validation_error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    error_logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": "internal_error"
        }
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("Application starting up...")
    db_logger.info("Database connection pool initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Application shutting down...")
    db_logger.info("Closing database connections") 