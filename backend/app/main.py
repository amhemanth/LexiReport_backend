import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from app.api.v1.api import api_router
from app.config.settings import get_settings
from app.db.session import get_db
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
    AIProcessingError
)
from app.core.model_cache import precache_models

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Pre-cache models at server startup
logger.info("Starting model pre-caching...")
precache_models()

# Set up middleware
setup_middleware(app)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(AuthenticationException, base_auth_handler)
app.add_exception_handler(PermissionException, base_permission_handler)
app.add_exception_handler(NotFoundException, base_not_found_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(LexiReportException, lexireport_exception_handler)
app.add_exception_handler(AIProcessingError, ai_processing_exception_handler)

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
        content={"detail": errors}
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR) 