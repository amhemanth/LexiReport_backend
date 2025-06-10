"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.redis import redis_manager
from app.core.logger import logger

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "components": {
            "database": "healthy",
            "redis": "healthy"
        }
    }
    
    # Check database connection
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Check Redis connection
    if not redis_manager.check_connection():
        logger.error("Redis health check failed")
        health_status["components"]["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    return health_status 