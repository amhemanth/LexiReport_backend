from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
from app.models.core.user import User
from app.schemas.audit import (
    AuditLogCreate, AuditLogResponse, AuditLogFilter,
    UserActivityCreate, UserActivityResponse,
    SystemMetricCreate, SystemMetricResponse,
    ErrorLogCreate, ErrorLogResponse
)
from app.services.audit import audit_service

router = APIRouter()

@router.get("/logs", response_model=List[AuditLogResponse])
@require_permissions([Permission.READ_AUDIT])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering."""
    filters = AuditLogFilter(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id
    )
    return audit_service.get_audit_logs_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit, filters=filters
    )

@router.post("/logs", response_model=AuditLogResponse)
@require_permissions([Permission.WRITE_AUDIT])
async def create_audit_log(
    log_in: AuditLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new audit log entry."""
    return audit_service.create_audit_log(
        db, user_id=current_user.id, obj_in=log_in
    )

@router.get("/activities", response_model=List[UserActivityResponse])
@require_permissions([Permission.READ_AUDIT])
async def get_user_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    activity_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user activities with optional filtering."""
    return audit_service.get_user_activities(
        db, user_id=current_user.id, skip=skip, limit=limit,
        activity_type=activity_type
    )

@router.post("/activities", response_model=UserActivityResponse)
@require_permissions([Permission.WRITE_AUDIT])
async def create_user_activity(
    activity_in: UserActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user activity entry."""
    return audit_service.create_user_activity(
        db, user_id=current_user.id, obj_in=activity_in
    )

@router.get("/metrics", response_model=List[SystemMetricResponse])
@require_permissions([Permission.VIEW_METRICS])
async def get_system_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    metric_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system metrics with optional filtering."""
    return audit_service.get_system_metrics_by_type(
        db, metric_type=metric_type, skip=skip, limit=limit
    )

@router.post("/metrics", response_model=SystemMetricResponse)
@require_permissions([Permission.WRITE_AUDIT])
async def create_system_metric(
    metric_in: SystemMetricCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new system metric entry."""
    return audit_service.create_system_metric(db, obj_in=metric_in)

@router.get("/errors", response_model=List[ErrorLogResponse])
@require_permissions([Permission.VIEW_ERRORS])
async def get_error_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    error_type: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get error logs with optional filtering."""
    return audit_service.get_error_logs_by_type(
        db, error_type=error_type, severity=severity,
        skip=skip, limit=limit
    )

@router.post("/errors", response_model=ErrorLogResponse)
@require_permissions([Permission.WRITE_AUDIT])
async def create_error_log(
    error_in: ErrorLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new error log entry."""
    return audit_service.create_error_log(
        db, user_id=current_user.id, obj_in=error_in
    ) 