from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.endpoints import auth, reports
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DocuInsight API",
    description="API for document analysis and insights",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log CORS settings
logger.debug(f"CORS Origins: {settings.CORS_ORIGINS}")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up DocuInsight API server...")
    logger.info(f"Server running at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"CORS enabled for origins: {settings.CORS_ORIGINS}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down DocuInsight API server...")

@app.get("/", response_class=JSONResponse)
async def root(request: Request):
    logger.info(f"Root endpoint accessed from: {request.client.host}")
    return {
        "message": "Welcome to DocuInsight API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 