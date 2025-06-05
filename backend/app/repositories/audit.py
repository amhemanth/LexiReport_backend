from sqlalchemy.orm import Session
from app.models.audit.audit_log import AuditLog
from app.models.analytics.user_activity import UserActivity
from app.models.analytics.system_metrics import SystemMetrics
from app.models.analytics.error_log import ErrorLog
from typing import List, Optional
import uuid

class AuditLogRepository:
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).offset(skip).limit(limit).all()

class UserActivityRepository:
    def get_by_user(self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[UserActivity]:
        return db.query(UserActivity).filter(UserActivity.user_id == user_id).offset(skip).limit(limit).all()

class SystemMetricsRepository:
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[SystemMetrics]:
        return db.query(SystemMetrics).offset(skip).limit(limit).all()

class ErrorLogRepository:
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ErrorLog]:
        return db.query(ErrorLog).offset(skip).limit(limit).all()

audit_log_repository = AuditLogRepository()
user_activity_repository = UserActivityRepository()
system_metrics_repository = SystemMetricsRepository()
error_log_repository = ErrorLogRepository() 