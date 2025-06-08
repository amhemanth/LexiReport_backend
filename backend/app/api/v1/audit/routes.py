from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
from app.models.core.user import User
from app.schemas.audit import (
    AuditLogCreate, AuditLogResponse, AuditLogFilter, AuditLogList,
    UserActivityCreate, UserActivityResponse, UserActivityList,
    SystemMetricsCreate, SystemMetricsResponse, SystemMetricsList,
    ErrorLogCreate, ErrorLogResponse, ErrorLogList
)
from app.services.audit import audit_service

router = APIRouter()

@router.get("/logs", response_model=AuditLogList)
@require_permissions([Permission.READ_AUDIT])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering."""
    filters = AuditLogFilter(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date
    )
    return await audit_service.get_audit_logs_by_filters(
        db, filters=filters, skip=skip, limit=limit
    )

@router.post("/logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_AUDIT])
async def create_audit_log(
    log: AuditLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new audit log entry."""
    return await audit_service.create_audit_log(db, obj_in=log)

@router.get("/activities", response_model=UserActivityList)
@require_permissions([Permission.READ_AUDIT])
async def get_user_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    activity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user activities with optional filtering."""
    return await audit_service.get_user_activities(
        db, user_id=current_user.id, skip=skip, limit=limit,
        activity_type=activity_type,
        start_date=start_date,
        end_date=end_date
    )

@router.post("/activities", response_model=UserActivityResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_AUDIT])
async def create_user_activity(
    activity: UserActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user activity entry."""
    return await audit_service.create_user_activity(
        db, user_id=current_user.id, obj_in=activity
    )

@router.get("/metrics", response_model=SystemMetricsList)
@require_permissions([Permission.VIEW_METRICS])
async def get_system_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    metric_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system metrics with optional filtering."""
    if start_date and end_date:
        return await audit_service.get_metrics_by_date_range(
            db, metric_name=metric_name,
            start_date=start_date, end_date=end_date,
            skip=skip, limit=limit
        )
    return await audit_service.get_system_metrics_by_name(
        db, metric_name=metric_name, skip=skip, limit=limit
    )

@router.post("/metrics", response_model=SystemMetricsResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_AUDIT])
async def create_system_metric(
    metric: SystemMetricsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new system metric entry."""
    return await audit_service.create_system_metric(db, obj_in=metric)

@router.get("/errors", response_model=ErrorLogList)
@require_permissions([Permission.VIEW_ERRORS])
async def get_error_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    error_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get error logs with optional filtering."""
    if start_date and end_date:
        return await audit_service.get_errors_by_date_range(
            db, error_type=error_type,
            start_date=start_date, end_date=end_date,
            skip=skip, limit=limit
        )
    return await audit_service.get_error_logs_by_type(
        db, error_type=error_type, skip=skip, limit=limit
    )

@router.post("/errors", response_model=ErrorLogResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_AUDIT])
async def create_error_log(
    error: ErrorLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new error log entry."""
    return await audit_service.create_error_log(db, obj_in=error) 