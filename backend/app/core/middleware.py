"""Middleware configuration."""
import time
import uuid
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import get_settings
from app.core.logger import (
    logger,
    api_logger,
    security_logger,
    error_logger
)
from app.core.redis import redis_manager

settings = get_settings()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing information."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to headers
        request.headers.__dict__["_list"].append(
            (b"x-request-id", request_id.encode())
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log request details
            api_logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "client_ip": request.client.host,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            
            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            error_logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                    "client_ip": request.client.host,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Skip security headers for docs
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            return response
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=(), interest-cohort=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        security_logger.debug(
            "Security headers added to response",
            extra={
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            # Get current request count
            current = redis_manager.get_key(key)
            if current is None:
                # First request
                redis_manager.set_key(key, 1, expire=60)  # 1 minute window
            elif int(current) >= settings.RATE_LIMIT_PER_MINUTE:
                # Rate limit exceeded
                error_logger.warning(
                    "Rate limit exceeded",
                    extra={
                        "client_ip": client_ip,
                        "path": request.url.path,
                        "current_count": current,
                        "limit": settings.RATE_LIMIT_PER_MINUTE
                    }
                )
                return Response(
                    content="Too many requests",
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            else:
                # Increment counter
                redis_manager.increment_key(key)
                
            return await call_next(request)
            
        except Exception as e:
            error_logger.error(
                "Rate limiting error",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "error": str(e)
                }
            )
            # On Redis error, allow the request to proceed
            return await call_next(request)

def setup_middleware(app: FastAPI) -> None:
    """Set up all middleware for the application."""
    
    # Add CORS middleware first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Request-ID"]
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # Add session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
        same_site="lax",
        https_only=settings.ENVIRONMENT == "production"  # Only enforce HTTPS in production
    )
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add rate limiting
    app.add_middleware(RateLimitMiddleware)
    
    # Add Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    logger.info("Middleware setup completed") 