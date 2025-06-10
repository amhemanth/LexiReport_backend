from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
import uuid

from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
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
    ReportList,
    ReportTypeResponse,
    ReportStatusResponse
)
from app.schemas.report_comment import (
    ReportCommentCreate,
    ReportCommentUpdate,
    ReportCommentResponse,
    ReportCommentList
)
from app.services.report import ReportService
from app.services.report_comment import report_comment_service
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


@router.get("/{report_id}/comments", response_model=ReportCommentList)
@require_permissions([Permission.READ_COMMENTS])
async def get_report_comments(
    report_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a report."""
    return await report_comment_service.get_comments_by_report(
        db, report_id=report_id, skip=skip, limit=limit
    )


@router.post("/{report_id}/comments", response_model=ReportCommentResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_COMMENTS])
async def create_report_comment(
    report_id: uuid.UUID,
    comment: ReportCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment on a report."""
    comment.report_id = report_id
    return await report_comment_service.create_comment(db, user_id=current_user.id, obj_in=comment)


@router.put("/comments/{comment_id}", response_model=ReportCommentResponse)
@require_permissions([Permission.WRITE_COMMENTS])
async def update_report_comment(
    comment_id: uuid.UUID,
    comment: ReportCommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a report comment."""
    return await report_comment_service.update_comment(
        db, comment_id=comment_id, obj_in=comment
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.WRITE_COMMENTS])
async def delete_report_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a report comment."""
    await report_comment_service.delete_comment(db, comment_id=comment_id)


@router.get("/comments/{comment_id}/replies", response_model=ReportCommentList)
@require_permissions([Permission.READ_COMMENTS])
async def get_report_comment_replies(
    comment_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get replies to a report comment."""
    return await report_comment_service.get_replies(
        db, comment_id=comment_id, skip=skip, limit=limit
    ) 