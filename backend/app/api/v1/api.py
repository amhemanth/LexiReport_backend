from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.users.routes import router as users_router
from app.api.v1.reports.routes import router as reports_router

api_router = APIRouter()

# Include routers under v1
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"]) 