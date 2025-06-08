from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.schemas.bi import (
    BIConnectionCreate, BIConnectionUpdate, BIConnectionResponse,
    BIDashboardCreate, BIDashboardUpdate, BIDashboardResponse,
    BIReportCreate, BIReportUpdate, BIReportResponse,
    SyncJobCreate, SyncJobUpdate, SyncJobResponse
)
from app.services.bi import bi_service
import uuid
from datetime import datetime

router = APIRouter()

# Connection routes
@router.get("/connections", response_model=List[BIConnectionResponse])
def list_bi_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    platform_type: Optional[str] = None
):
    """List BI connections."""
    if platform_type:
        return bi_service.get_connections_by_platform(
            db, platform_type=platform_type, skip=skip, limit=limit
        )
    return bi_service.get_connections_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.get("/connections/{connection_id}", response_model=BIConnectionResponse)
def get_bi_connection(
    connection_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a BI connection by ID."""
    connection = bi_service.get_connection(db, id=connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BI connection not found"
        )
    return connection

@router.post("/connections", response_model=BIConnectionResponse)
def create_bi_connection(
    obj_in: BIConnectionCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new BI connection."""
    return bi_service.create_connection(db, obj_in=obj_in)

@router.put("/connections/{connection_id}", response_model=BIConnectionResponse)
def update_bi_connection(
    connection_id: uuid.UUID,
    obj_in: BIConnectionUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a BI connection."""
    return bi_service.update_connection(db, id=connection_id, obj_in=obj_in)

@router.delete("/connections/{connection_id}", response_model=BIConnectionResponse)
def delete_bi_connection(
    connection_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a BI connection."""
    return bi_service.delete_connection(db, id=connection_id)

# Dashboard routes
@router.get("/dashboards", response_model=List[BIDashboardResponse])
def list_dashboards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    connection_id: Optional[uuid.UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List BI dashboards."""
    if connection_id:
        return bi_service.get_dashboards_by_connection(
            db, connection_id=connection_id, skip=skip, limit=limit
        )
    return []

@router.get("/dashboards/{dashboard_id}", response_model=BIDashboardResponse)
def get_dashboard(
    dashboard_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a BI dashboard by ID."""
    dashboard = bi_service.get_dashboard(db, id=dashboard_id)
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BI dashboard not found"
        )
    return dashboard

@router.post("/dashboards", response_model=BIDashboardResponse)
def create_dashboard(
    obj_in: BIDashboardCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new BI dashboard."""
    return bi_service.create_dashboard(db, obj_in=obj_in)

@router.put("/dashboards/{dashboard_id}", response_model=BIDashboardResponse)
def update_dashboard(
    dashboard_id: uuid.UUID,
    obj_in: BIDashboardUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a BI dashboard."""
    return bi_service.update_dashboard(db, id=dashboard_id, obj_in=obj_in)

@router.delete("/dashboards/{dashboard_id}", response_model=BIDashboardResponse)
def delete_dashboard(
    dashboard_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a BI dashboard."""
    return bi_service.delete_dashboard(db, id=dashboard_id)

# Report routes
@router.get("/reports", response_model=List[BIReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dashboard_id: Optional[uuid.UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List BI reports."""
    if dashboard_id:
        return bi_service.get_reports_by_dashboard(
            db, dashboard_id=dashboard_id, skip=skip, limit=limit
        )
    return []

@router.get("/reports/{report_id}", response_model=BIReportResponse)
def get_report(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a BI report by ID."""
    report = bi_service.get_report(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BI report not found"
        )
    return report

@router.post("/reports", response_model=BIReportResponse)
def create_report(
    obj_in: BIReportCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new BI report."""
    return bi_service.create_report(db, obj_in=obj_in)

@router.put("/reports/{report_id}", response_model=BIReportResponse)
def update_report(
    report_id: uuid.UUID,
    obj_in: BIReportUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a BI report."""
    return bi_service.update_report(db, id=report_id, obj_in=obj_in)

@router.delete("/reports/{report_id}", response_model=BIReportResponse)
def delete_report(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a BI report."""
    return bi_service.delete_report(db, id=report_id)

# Sync job routes
@router.get("/sync-jobs", response_model=List[SyncJobResponse])
def list_sync_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    connection_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List sync jobs."""
    if status:
        return bi_service.get_sync_jobs_by_status(
            db, status=status, skip=skip, limit=limit
        )
    if connection_id:
        return bi_service.get_sync_jobs_by_connection(
            db, connection_id=connection_id, skip=skip, limit=limit
        )
    return []

@router.get("/sync-jobs/{job_id}", response_model=SyncJobResponse)
def get_sync_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a sync job by ID."""
    job = bi_service.get_sync_job(db, id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync job not found"
        )
    return job

@router.post("/sync-jobs", response_model=SyncJobResponse)
def create_sync_job(
    obj_in: SyncJobCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sync job."""
    return bi_service.create_sync_job(db, obj_in=obj_in)

@router.put("/sync-jobs/{job_id}", response_model=SyncJobResponse)
def update_sync_job(
    job_id: uuid.UUID,
    obj_in: SyncJobUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sync job."""
    return bi_service.update_sync_job(db, id=job_id, obj_in=obj_in)

@router.delete("/sync-jobs/{job_id}", response_model=SyncJobResponse)
def delete_sync_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a sync job."""
    return bi_service.delete_sync_job(db, id=job_id) 