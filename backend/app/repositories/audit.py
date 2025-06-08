from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit.audit_log import AuditLog
from app.models.analytics.user_activity import UserActivity
from app.models.analytics.system_metrics import SystemMetrics
from app.models.analytics.error_log import ErrorLog
from app.schemas.audit import (
    AuditLogCreate, AuditLogUpdate,
    UserActivityCreate, UserActivityUpdate,
    SystemMetricsCreate, SystemMetricsUpdate,
    ErrorLogCreate, ErrorLogUpdate
)
from .base import BaseRepository

class AuditLogRepository(
    BaseRepository[AuditLog, AuditLogCreate, AuditLogUpdate]
):
    """Repository for AuditLog model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_action(
        self, db: Session, *, action: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by action."""
        return self.get_multi_by_field(
            db, field="action", value=action, skip=skip, limit=limit
        )

    def get_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by entity."""
        return db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).offset(skip).limit(limit).all()

class UserActivityRepository(
    BaseRepository[UserActivity, UserActivityCreate, UserActivityUpdate]
):
    """Repository for UserActivity model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[UserActivity]:
        """Get user activities by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_activity_type(
        self, db: Session, *, activity_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[UserActivity]:
        """Get user activities by type."""
        return self.get_multi_by_field(
            db, field="activity_type", value=activity_type,
            skip=skip, limit=limit
        )

class SystemMetricsRepository(
    BaseRepository[SystemMetrics, SystemMetricsCreate, SystemMetricsUpdate]
):
    """Repository for SystemMetrics model."""

    def get_by_metric_type(
        self, db: Session, *, metric_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[SystemMetrics]:
        """Get system metrics by type."""
        return self.get_multi_by_field(
            db, field="metric_type", value=metric_type,
            skip=skip, limit=limit
        )

class ErrorLogRepository(
    BaseRepository[ErrorLog, ErrorLogCreate, ErrorLogUpdate]
):
    """Repository for ErrorLog model."""

    def get_by_error_type(
        self, db: Session, *, error_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[ErrorLog]:
        """Get error logs by type."""
        return self.get_multi_by_field(
            db, field="error_type", value=error_type,
            skip=skip, limit=limit
        )

    def get_by_severity(
        self, db: Session, *, severity: str,
        skip: int = 0, limit: int = 100
    ) -> List[ErrorLog]:
        """Get error logs by severity."""
        return self.get_multi_by_field(
            db, field="severity", value=severity,
            skip=skip, limit=limit
        )

# Create repository instances
audit_log_repository = AuditLogRepository(AuditLog)
user_activity_repository = UserActivityRepository(UserActivity)
system_metrics_repository = SystemMetricsRepository(SystemMetrics)
error_log_repository = ErrorLogRepository(ErrorLog) 