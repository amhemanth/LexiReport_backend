from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.users.routes import router as users_router
from app.api.v1.reports.routes import router as reports_router
from app.api.v1.voice.routes import router as voice_router
from app.api.v1.reports.insights import router as report_insights_router
from app.api.v1.notifications.routes import router as notifications_router
from app.api.v1.files.routes import router as files_router
from app.api.v1.comments.routes import router as comments_router
from app.api.v1.audit.routes import router as audit_router
from app.api.v1.bi.routes import router as bi_router
from app.api.v1.offline.routes import router as offline_router
from app.api.v1.tags.routes import router as tags_router
from app.api.v1.analytics.routes import router as analytics_router
from app.api.v1.ai.routes import router as ai_router

api_router = APIRouter()

# Include routers under v1
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(voice_router, prefix="/voice", tags=["Voice"])
api_router.include_router(report_insights_router, prefix="/reports", tags=["ReportInsights"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(files_router, prefix="/files", tags=["Files"])
api_router.include_router(comments_router, prefix="/comments", tags=["Comments"])
api_router.include_router(audit_router, prefix="/audit", tags=["Audit"])
api_router.include_router(bi_router, prefix="/bi", tags=["Business Intelligence"])
api_router.include_router(offline_router, prefix="/offline", tags=["Offline Content"])
api_router.include_router(tags_router, prefix="/tags", tags=["Tags"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Services"]) 