import os
from typing import List, Optional, Tuple, BinaryIO, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import mimetypes
import uuid

from app.models.core.user import User
from app.models.reports import (
    Report,
    ReportType,
    ReportStatus,
    ReportTypeCategory,
    AnalysisType,
    MetadataType,
    ReportInsight,
    ReportQuery,
    ReportContent,
    ReportVersion
)
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportTypeResponse,
    ReportStatusResponse
)
from app.repositories.report import report_repository
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
        report_in: ReportCreate
    ) -> ReportResponse:
        """Create a new report."""
        report_data = report_in.dict()
        report_data["created_by"] = user.id
        report_data["updated_by"] = user.id
        
        report = report_repository.create(self.db, obj_in=report_data)
        return ReportResponse.from_orm(report)

    async def list_reports(
        self,
        user: User,
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
        query = self.db.query(Report)
        
        # Apply filters
        if type:
            query = query.filter(Report.type == type)
        if category:
            query = query.filter(Report.category == category)
        if status:
            query = query.filter(Report.status == status)
        if analysis_type:
            query = query.filter(Report.analysis_type == analysis_type)
        if metadata_type:
            query = query.filter(Report.metadata_type == metadata_type)
        if is_archived is not None:
            query = query.filter(Report.is_archived == is_archived)
        if is_public is not None:
            query = query.filter(Report.is_public == is_public)
            
        # Get user's reports and shared reports
        reports = (
            query.filter(
                (Report.created_by == user.id) |
                (Report.is_public == True)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [ReportResponse.from_orm(report) for report in reports]

    async def get_report(
        self,
        user: User,
        report_id: uuid.UUID
    ) -> Optional[ReportResponse]:
        """Get a specific report."""
        report = report_repository.get(self.db, id=report_id)
        if not report:
            return None
            
        # Check access
        if report.created_by != user.id and not report.is_public:
            return None
            
        return ReportResponse.from_orm(report)

    async def update_report(
        self,
        user: User,
        report_id: uuid.UUID,
        report_in: ReportUpdate
    ) -> Optional[ReportResponse]:
        """Update a report."""
        report = report_repository.get(self.db, id=report_id)
        if not report:
            return None
            
        # Check access
        if report.created_by != user.id:
            return None

        update_data = report_in.dict(exclude_unset=True)
        update_data["updated_by"] = user.id
        
        report = report_repository.update(self.db, db_obj=report, obj_in=update_data)
        return ReportResponse.from_orm(report)

    async def delete_report(
        self,
        user: User,
        report_id: uuid.UUID
    ) -> bool:
        """Delete a report."""
        report = report_repository.get(self.db, id=report_id)
        if not report:
            return False
            
        # Check access
        if report.created_by != user.id:
            return False

        report_repository.remove(self.db, id=report_id)
        return True

    async def archive_report(
        self,
        user: User,
        report_id: uuid.UUID
    ) -> Optional[ReportResponse]:
        """Archive a report."""
        report = report_repository.get(self.db, id=report_id)
        if not report:
            return None
            
        # Check access
        if report.created_by != user.id:
            return None

        update_data = {"is_archived": True, "updated_by": user.id}
        report = report_repository.update(self.db, db_obj=report, obj_in=update_data)
        return ReportResponse.from_orm(report)

    async def unarchive_report(
        self,
        user: User,
        report_id: uuid.UUID
    ) -> Optional[ReportResponse]:
        """Unarchive a report."""
        report = report_repository.get(self.db, id=report_id)
        if not report:
            return None
            
        # Check access
        if report.created_by != user.id:
            return None

        update_data = {"is_archived": False, "updated_by": user.id}
        report = report_repository.update(self.db, db_obj=report, obj_in=update_data)
        return ReportResponse.from_orm(report)

    async def make_public(
        self,
        user: User,
        report_id: uuid.UUID
    ) -> Optional[ReportResponse]:
        """Make a report public."""
        report = report_repository.get(self.db, id=report_id)
        if not report:
            return None
            
        # Check access
        if report.created_by != user.id:
            return None

        update_data = {"is_public": True, "updated_by": user.id}
        report = report_repository.update(self.db, db_obj=report, obj_in=update_data)
        return ReportResponse.from_orm(report)

    async def make_private(
        self,
        user: User,
        report_id: uuid.UUID
    ) -> Optional[ReportResponse]:
        """Make a report private."""
        report = report_repository.get(self.db, id=report_id)
        if not report:
            return None
            
        # Check access
        if report.created_by != user.id:
            return None

        update_data = {"is_public": False, "updated_by": user.id}
        report = report_repository.update(self.db, db_obj=report, obj_in=update_data)
        return ReportResponse.from_orm(report)

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