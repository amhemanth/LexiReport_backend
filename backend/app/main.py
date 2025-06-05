import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.v1.api import api_router
from app.config.settings import get_settings
from app.core.handlers import (
    validation_exception_handler,
    general_exception_handler,
    lexireport_exception_handler,
    base_validation_handler,
    base_auth_handler,
    base_permission_handler,
    base_not_found_handler
)
from app.core.middleware import setup_middleware
from app.core.exceptions import (
    LexiReportException,
    ValidationException,
    AuthenticationException,
    PermissionException,
    NotFoundException
)

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

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

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
app.add_exception_handler(ValidationException, base_validation_handler)
app.add_exception_handler(AuthenticationException, base_auth_handler)
app.add_exception_handler(PermissionException, base_permission_handler)
app.add_exception_handler(NotFoundException, base_not_found_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(LexiReportException, lexireport_exception_handler)

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
def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs") 