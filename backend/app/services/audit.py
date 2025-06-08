from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.audit import (
    audit_log_repository,
    system_metrics_repository,
    error_log_repository
)
from app.models.audit.audit_log import AuditLog
from app.models.analytics.system_metrics import SystemMetrics
from app.models.analytics.error_log import ErrorLog
from app.schemas.audit import (
    AuditLogCreate, AuditLogUpdate,
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

    def get_system_metrics_by_name(
        self, db: Session, *, metric_name: str,
        skip: int = 0, limit: int = 100
    ) -> List[SystemMetrics]:
        """Get system metrics by name."""
        return system_metrics_repository.get_by_metric_name(
            db, metric_name=metric_name, skip=skip, limit=limit
        )

    def get_latest_metrics(
        self, db: Session, *, metric_name: str, limit: int = 100
    ) -> List[SystemMetrics]:
        """Get latest system metrics by name."""
        return system_metrics_repository.get_latest_metrics(
            db, metric_name=metric_name, limit=limit
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

    def get_latest_errors(
        self, db: Session, *, error_type: str, limit: int = 100
    ) -> List[ErrorLog]:
        """Get latest error logs by type."""
        return error_log_repository.get_latest_errors(
            db, error_type=error_type, limit=limit
        )

    def create_error_log(
        self, db: Session, *, obj_in: ErrorLogCreate
    ) -> ErrorLog:
        """Create a new error log entry."""
        return error_log_repository.create(db, obj_in=obj_in)

# Create service instance
audit_service = AuditService() 