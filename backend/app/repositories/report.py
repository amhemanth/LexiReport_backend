from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.models.reports import (
    Report, ReportShare, ReportTemplate, ReportSchedule,
    ReportExport, ReportType, ReportStatus, ReportTypeCategory,
    AnalysisType, MetadataType
)
from app.schemas.report import (
    ReportCreate, ReportUpdate, ReportShareCreate, ReportShareUpdate,
    ReportTemplateCreate, ReportTemplateUpdate,
    ReportScheduleCreate, ReportScheduleUpdate,
    ReportExportCreate, ReportExportUpdate
)
from .base import BaseRepository

class ReportRepository(BaseRepository[Report, ReportCreate, ReportUpdate]):
    """Repository for Report model."""

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports created by user."""
        return self.get_multi_by_field(
            db, field="created_by", value=user_id, skip=skip, limit=limit
        )

    def get_shared_with_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports shared with user."""
        return db.query(Report).join(
            ReportShare, Report.id == ReportShare.report_id
        ).filter(
            ReportShare.shared_with == user_id
        ).offset(skip).limit(limit).all()

    def get_by_type(
        self, db: Session, *, type: ReportType,
        skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports by type."""
        return self.get_multi_by_field(
            db, field="type", value=type, skip=skip, limit=limit
        )

    def get_by_status(
        self, db: Session, *, status: ReportStatus,
        skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports by status."""
        return self.get_multi_by_field(
            db, field="status", value=status, skip=skip, limit=limit
        )

    def get_by_category(
        self, db: Session, *, category: ReportTypeCategory,
        skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports by category."""
        return self.get_multi_by_field(
            db, field="category", value=category, skip=skip, limit=limit
        )

    def get_by_analysis_type(
        self, db: Session, *, analysis_type: AnalysisType,
        skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports by analysis type."""
        return self.get_multi_by_field(
            db, field="analysis_type", value=analysis_type, skip=skip, limit=limit
        )

    def get_by_metadata_type(
        self, db: Session, *, metadata_type: MetadataType,
        skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports by metadata type."""
        return self.get_multi_by_field(
            db, field="metadata_type", value=metadata_type, skip=skip, limit=limit
        )

    def get_by_template(
        self, db: Session, *, template_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports by template."""
        return self.get_multi_by_field(
            db, field="template_id", value=template_id, skip=skip, limit=limit
        )

    def get_archived(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get archived reports."""
        return self.get_multi_by_field(
            db, field="is_archived", value=True, skip=skip, limit=limit
        )

    def get_public(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get public reports."""
        return self.get_multi_by_field(
            db, field="is_public", value=True, skip=skip, limit=limit
        )

class ReportShareRepository(BaseRepository[ReportShare, ReportShareCreate, ReportShareUpdate]):
    """Repository for ReportShare model."""

    def get_by_report(
        self, db: Session, *, report_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportShare]:
        """Get shares for a report."""
        return self.get_multi_by_field(
            db, field="report_id", value=report_id, skip=skip, limit=limit
        )

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportShare]:
        """Get shares for a user."""
        return self.get_multi_by_field(
            db, field="shared_with", value=user_id, skip=skip, limit=limit
        )

class ReportTemplateRepository(BaseRepository[ReportTemplate, ReportTemplateCreate, ReportTemplateUpdate]):
    """Repository for ReportTemplate model."""

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportTemplate]:
        """Get templates created by user."""
        return self.get_multi_by_field(
            db, field="created_by", value=user_id, skip=skip, limit=limit
        )

    def get_by_type(
        self, db: Session, *, report_type: ReportType,
        skip: int = 0, limit: int = 100
    ) -> List[ReportTemplate]:
        """Get templates by report type."""
        return self.get_multi_by_field(
            db, field="report_type", value=report_type, skip=skip, limit=limit
        )

class ReportScheduleRepository(BaseRepository[ReportSchedule, ReportScheduleCreate, ReportScheduleUpdate]):
    """Repository for ReportSchedule model."""

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportSchedule]:
        """Get schedules created by user."""
        return self.get_multi_by_field(
            db, field="created_by", value=user_id, skip=skip, limit=limit
        )

    def get_active_schedules(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ReportSchedule]:
        """Get active schedules."""
        return self.get_multi_by_field(
            db, field="is_active", value=True, skip=skip, limit=limit
        )

class ReportExportRepository(BaseRepository[ReportExport, ReportExportCreate, ReportExportUpdate]):
    """Repository for ReportExport model."""

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportExport]:
        """Get exports created by user."""
        return self.get_multi_by_field(
            db, field="created_by", value=user_id, skip=skip, limit=limit
        )

    def get_by_report(
        self, db: Session, *, report_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportExport]:
        """Get exports for a report."""
        return self.get_multi_by_field(
            db, field="report_id", value=report_id, skip=skip, limit=limit
        )

# Create repository instances
report_repository = ReportRepository(Report)
report_share_repository = ReportShareRepository(ReportShare)
report_template_repository = ReportTemplateRepository(ReportTemplate)
report_schedule_repository = ReportScheduleRepository(ReportSchedule)
report_export_repository = ReportExportRepository(ReportExport) 