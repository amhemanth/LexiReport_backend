import os
from typing import List, Optional, Tuple, BinaryIO
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import mimetypes

from app.models.core.user import User
from app.models.reports import (
    Report,
    ReportType,
    ReportStatus,
    ReportInsight,
    ReportQuery
)
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportTypeResponse,
    ReportStatusResponse
)
from app.config.settings import get_settings
from app.config.storage_settings import get_storage_settings

settings = get_settings()
storage_settings = get_storage_settings()


class ReportService:
    """Service for handling report operations."""

    def __init__(self, db: Session):
        self.db = db

    async def create_report(
        self,
        user: User,
        file: UploadFile,
        report_in: ReportCreate
    ) -> ReportResponse:
        """Create a new report."""
        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
        if file_ext not in storage_settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {storage_settings.ALLOWED_EXTENSIONS}"
            )

        # Validate file size
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        if file_size > storage_settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {storage_settings.MAX_UPLOAD_SIZE} bytes"
            )

        # Save file
        file_path = os.path.join(storage_settings.UPLOAD_DIR, f"{user.id}_{file.filename}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Create report
        report = Report(
            user_id=user.id,
            title=report_in.title,
            description=report_in.description,
            file_path=file_path,
            file_type=file_ext,
            file_size=file_size,
            report_type_id=report_in.report_type_id,
            status_id=1,  # Initial status: uploaded
            metadata=report_in.metadata
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return ReportResponse.from_orm(report)

    async def list_reports(
        self,
        user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReportResponse]:
        """List all reports for a user."""
        reports = (
            self.db.query(Report)
            .filter(Report.user_id == user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [ReportResponse.from_orm(report) for report in reports]

    async def get_report(
        self,
        user: User,
        report_id: int
    ) -> Optional[ReportResponse]:
        """Get a specific report."""
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user.id)
            .first()
        )
        if not report:
            return None
        return ReportResponse.from_orm(report)

    async def update_report(
        self,
        user: User,
        report_id: int,
        report_in: ReportUpdate
    ) -> Optional[ReportResponse]:
        """Update a report."""
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user.id)
            .first()
        )
        if not report:
            return None

        update_data = report_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(report, field, value)

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return ReportResponse.from_orm(report)

    async def delete_report(
        self,
        user: User,
        report_id: int
    ) -> bool:
        """Delete a report."""
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user.id)
            .first()
        )
        if not report:
            return False

        # Delete file
        if os.path.exists(report.file_path):
            os.remove(report.file_path)

        self.db.delete(report)
        self.db.commit()

        return True

    async def list_report_types(self) -> List[ReportTypeResponse]:
        """List all report types."""
        report_types = self.db.query(ReportType).all()
        return [ReportTypeResponse.from_orm(rt) for rt in report_types]

    async def list_report_statuses(self) -> List[ReportStatusResponse]:
        """List all report statuses."""
        report_statuses = self.db.query(ReportStatus).all()
        return [ReportStatusResponse.from_orm(rs) for rs in report_statuses]

    async def get_file_content(
        self,
        user: User,
        report_id: int
    ) -> Tuple[BinaryIO, str, str]:
        """Get file content for streaming.
        
        Returns:
            Tuple[BinaryIO, str, str]: File object, filename, and content type
        """
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user.id)
            .first()
        )
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if not os.path.exists(report.file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Get content type
        content_type, _ = mimetypes.guess_type(report.file_path)
        if not content_type:
            content_type = "application/octet-stream"

        # Get original filename
        original_filename = os.path.basename(report.file_path)
        if original_filename.startswith(f"{user.id}_"):
            original_filename = original_filename[len(f"{user.id}_"):]

        return open(report.file_path, "rb"), original_filename, content_type

    async def get_file_metadata(
        self,
        user: User,
        report_id: int
    ) -> dict:
        """Get file metadata.
        
        Returns:
            dict: File metadata including size, type, and last modified time
        """
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user.id)
            .first()
        )
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if not os.path.exists(report.file_path):
            raise HTTPException(status_code=404, detail="File not found")

        file_stat = os.stat(report.file_path)
        return {
            "size": file_stat.st_size,
            "type": report.file_type,
            "last_modified": file_stat.st_mtime,
            "created_at": file_stat.st_ctime,
            "path": report.file_path
        }

    async def stream_file(
        self,
        user: User,
        report_id: int
    ) -> StreamingResponse:
        """Stream file content.
        
        Returns:
            StreamingResponse: FastAPI streaming response
        """
        file_obj, filename, content_type = await self.get_file_content(user, report_id)
        
        return StreamingResponse(
            file_obj,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        ) 