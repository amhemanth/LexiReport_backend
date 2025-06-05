from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.users.routes import router as users_router
from app.api.v1.reports.routes import router as reports_router
from app.api.v1.voice.routes import router as voice_router
from app.api.v1.reports.insights import router as report_insights_router
from app.api.v1.notifications.routes import router as notifications_router

api_router = APIRouter()

# Include routers under v1
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(voice_router, prefix="/voice", tags=["Voice"])
api_router.include_router(report_insights_router, prefix="/reports", tags=["ReportInsights"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"]) 