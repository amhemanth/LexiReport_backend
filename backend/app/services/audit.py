from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.audit import (
    audit_log_repository,
    user_activity_repository,
    system_metrics_repository,
    error_log_repository
)
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
from app.core.exceptions import NotFoundException, PermissionException

class AuditService:
    """Service for managing audit logs and related operations."""

    def get_audit_logs_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by user."""
        return audit_log_repository.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

    def get_audit_logs_by_action(
        self, db: Session, *, action: str, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by action."""
        return audit_log_repository.get_by_action(
            db, action=action, skip=skip, limit=limit
        )

    def get_audit_logs_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by entity."""
        return audit_log_repository.get_by_entity(
            db, entity_type=entity_type, entity_id=entity_id,
            skip=skip, limit=limit
        )

    def create_audit_log(
        self, db: Session, *, obj_in: AuditLogCreate
    ) -> AuditLog:
        """Create a new audit log entry."""
        return audit_log_repository.create(db, obj_in=obj_in)

    def get_user_activities(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[UserActivity]:
        """Get user activities by user."""
        return user_activity_repository.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

    def get_activities_by_type(
        self, db: Session, *, activity_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[UserActivity]:
        """Get user activities by type."""
        return user_activity_repository.get_by_activity_type(
            db, activity_type=activity_type, skip=skip, limit=limit
        )

    def create_user_activity(
        self, db: Session, *, obj_in: UserActivityCreate
    ) -> UserActivity:
        """Create a new user activity entry."""
        return user_activity_repository.create(db, obj_in=obj_in)

    def get_system_metrics_by_type(
        self, db: Session, *, metric_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[SystemMetrics]:
        """Get system metrics by type."""
        return system_metrics_repository.get_by_metric_type(
            db, metric_type=metric_type, skip=skip, limit=limit
        )

    def create_system_metric(
        self, db: Session, *, obj_in: SystemMetricsCreate
    ) -> SystemMetrics:
        """Create a new system metric entry."""
        return system_metrics_repository.create(db, obj_in=obj_in)

    def get_error_logs_by_type(
        self, db: Session, *, error_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[ErrorLog]:
        """Get error logs by type."""
        return error_log_repository.get_by_error_type(
            db, error_type=error_type, skip=skip, limit=limit
        )

    def get_error_logs_by_severity(
        self, db: Session, *, severity: str,
        skip: int = 0, limit: int = 100
    ) -> List[ErrorLog]:
        """Get error logs by severity."""
        return error_log_repository.get_by_severity(
            db, severity=severity, skip=skip, limit=limit
        )

    def create_error_log(
        self, db: Session, *, obj_in: ErrorLogCreate
    ) -> ErrorLog:
        """Create a new error log entry."""
        return error_log_repository.create(db, obj_in=obj_in)

# Create service instance
audit_service = AuditService() 