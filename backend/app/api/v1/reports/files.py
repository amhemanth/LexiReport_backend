from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.services.report import ReportService

router = APIRouter()

@router.get("/{report_id}/file")
async def download_file(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a report file."""
    report_service = ReportService(db)
    return await report_service.stream_file(current_user, report_id)

@router.get("/{report_id}/metadata")
async def get_file_metadata(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get file metadata."""
    report_service = ReportService(db)
    return await report_service.get_file_metadata(current_user, report_id) 