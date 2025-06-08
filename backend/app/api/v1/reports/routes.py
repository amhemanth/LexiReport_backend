from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.models.reports import (
    Report,
    ReportType,
    ReportStatus,
    ReportTypeCategory,
    AnalysisType,
    MetadataType
)
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
    report_in: ReportCreate
) -> ReportResponse:
    """Create a new report."""
    report_service = ReportService(db)
    return await report_service.create_report(current_user, report_in)


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    type: Optional[ReportType] = None,
    category: Optional[ReportTypeCategory] = None,
    status: Optional[ReportStatus] = None,
    analysis_type: Optional[AnalysisType] = None,
    metadata_type: Optional[MetadataType] = None,
    is_archived: Optional[bool] = None,
    is_public: Optional[bool] = None
) -> List[ReportResponse]:
    """List reports with optional filters."""
    report_service = ReportService(db)
    return await report_service.list_reports(
        current_user,
        skip=skip,
        limit=limit,
        type=type,
        category=category,
        status=status,
        analysis_type=analysis_type,
        metadata_type=metadata_type,
        is_archived=is_archived,
        is_public=is_public
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: uuid.UUID
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
    report_id: uuid.UUID,
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
    report_id: uuid.UUID
) -> dict:
    """Delete a report."""
    report_service = ReportService(db)
    success = await report_service.delete_report(current_user, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "success"}


@router.post("/{report_id}/archive", response_model=ReportResponse)
async def archive_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: uuid.UUID
) -> ReportResponse:
    """Archive a report."""
    report_service = ReportService(db)
    report = await report_service.archive_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{report_id}/unarchive", response_model=ReportResponse)
async def unarchive_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: uuid.UUID
) -> ReportResponse:
    """Unarchive a report."""
    report_service = ReportService(db)
    report = await report_service.unarchive_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{report_id}/public", response_model=ReportResponse)
async def make_public(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: uuid.UUID
) -> ReportResponse:
    """Make a report public."""
    report_service = ReportService(db)
    report = await report_service.make_public(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{report_id}/private", response_model=ReportResponse)
async def make_private(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_id: uuid.UUID
) -> ReportResponse:
    """Make a report private."""
    report_service = ReportService(db)
    report = await report_service.make_private(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


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