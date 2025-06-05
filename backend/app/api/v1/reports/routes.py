from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.report import Report, ReportType, ReportStatus
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportTypeResponse,
    ReportStatusResponse
)
from app.services.report import ReportService
from app.api.v1.reports.files import router as files_router
from app.api.v1.reports.insights import router as insights_router

router = APIRouter()
router.include_router(files_router, prefix="/files", tags=["files"])
router.include_router(insights_router, prefix="/insights", tags=["insights"])


@router.post("/", response_model=ReportResponse)
async def create_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    report_in: ReportCreate
) -> ReportResponse:
    """Create a new report."""
    report_service = ReportService(db)
    return await report_service.create_report(current_user, file, report_in)


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> List[ReportResponse]:
    """List all reports for the current user."""
    report_service = ReportService(db)
    return await report_service.list_reports(current_user, skip, limit)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: int
) -> ReportResponse:
    """Get a specific report."""
    report_service = ReportService(db)
    report = await report_service.get_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: int,
    report_in: ReportUpdate
) -> ReportResponse:
    """Update a report."""
    report_service = ReportService(db)
    report = await report_service.update_report(current_user, report_id, report_in)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/{report_id}")
async def delete_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: int
) -> dict:
    """Delete a report."""
    report_service = ReportService(db)
    success = await report_service.delete_report(current_user, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "success"}


@router.get("/types/", response_model=List[ReportTypeResponse])
async def list_report_types(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportTypeResponse]:
    """List all report types."""
    report_service = ReportService(db)
    return await report_service.list_report_types()


@router.get("/statuses/", response_model=List[ReportStatusResponse])
async def list_report_statuses(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportStatusResponse]:
    """List all report statuses."""
    report_service = ReportService(db)
    return await report_service.list_report_statuses() 