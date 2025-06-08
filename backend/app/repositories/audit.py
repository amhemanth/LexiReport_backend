from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.models.audit.audit_log import AuditLog
from app.models.analytics.system_metrics import SystemMetrics
from app.models.analytics.error_log import ErrorLog
from app.schemas.audit import (
    AuditLogCreate, AuditLogUpdate,
    SystemMetricsCreate, SystemMetricsUpdate,
    ErrorLogCreate, ErrorLogUpdate,
    AuditLogFilter
)
from .base import BaseRepository

class AuditLogRepository(
    BaseRepository[AuditLog, AuditLogCreate, AuditLogUpdate]
):
    """Repository for AuditLog model."""

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
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
        self, db: Session, *, entity_type: str, entity_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by entity."""
        return db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).offset(skip).limit(limit).all()

    def get_by_filters(
        self, db: Session, *, filters: AuditLogFilter,
        skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by filters."""
        query = db.query(AuditLog)
        
        if filters.action:
            query = query.filter(AuditLog.action == filters.action)
        if filters.entity_type:
            query = query.filter(AuditLog.entity_type == filters.entity_type)
        if filters.entity_id:
            query = query.filter(AuditLog.entity_id == filters.entity_id)
        if filters.user_id:
            query = query.filter(AuditLog.user_id == filters.user_id)
        if filters.start_date:
            query = query.filter(AuditLog.created_at >= filters.start_date)
        if filters.end_date:
            query = query.filter(AuditLog.created_at <= filters.end_date)
            
        return query.offset(skip).limit(limit).all()

class SystemMetricsRepository(
    BaseRepository[SystemMetrics, SystemMetricsCreate, SystemMetricsUpdate]
):
    """Repository for SystemMetrics model."""

    def get_by_metric_name(
        self, db: Session, *, metric_name: str,
        skip: int = 0, limit: int = 100
    ) -> List[SystemMetrics]:
        """Get system metrics by name."""
        return self.get_multi_by_field(
            db, field="metric_name", value=metric_name,
            skip=skip, limit=limit
        )

    def get_latest_metrics(
        self, db: Session, *, metric_name: str, limit: int = 100
    ) -> List[SystemMetrics]:
        """Get latest system metrics by name."""
        return db.query(SystemMetrics).filter(
            SystemMetrics.metric_name == metric_name
        ).order_by(SystemMetrics.created_at.desc()).limit(limit).all()

    def get_metrics_by_date_range(
        self, db: Session, *, metric_name: str,
        start_date: datetime, end_date: datetime,
        skip: int = 0, limit: int = 100
    ) -> List[SystemMetrics]:
        """Get system metrics by date range."""
        return db.query(SystemMetrics).filter(
            SystemMetrics.metric_name == metric_name,
            SystemMetrics.created_at >= start_date,
            SystemMetrics.created_at <= end_date
        ).offset(skip).limit(limit).all()

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

    def get_latest_errors(
        self, db: Session, *, error_type: str, limit: int = 100
    ) -> List[ErrorLog]:
        """Get latest error logs by type."""
        return db.query(ErrorLog).filter(
            ErrorLog.error_type == error_type
        ).order_by(ErrorLog.created_at.desc()).limit(limit).all()

    def get_errors_by_date_range(
        self, db: Session, *, error_type: str,
        start_date: datetime, end_date: datetime,
        skip: int = 0, limit: int = 100
    ) -> List[ErrorLog]:
        """Get error logs by date range."""
        return db.query(ErrorLog).filter(
            ErrorLog.error_type == error_type,
            ErrorLog.created_at >= start_date,
            ErrorLog.created_at <= end_date
        ).offset(skip).limit(limit).all()

# Create repository instances
audit_log_repository = AuditLogRepository(AuditLog)
system_metrics_repository = SystemMetricsRepository(SystemMetrics)
error_log_repository = ErrorLogRepository(ErrorLog) 