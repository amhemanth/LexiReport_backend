from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.bi import (
    bi_connection_repository,
    bi_dashboard_repository,
    bi_report_repository,
    sync_job_repository
)
from app.models.integration.bi_integration import (
    BIConnection,
    BIDashboard,
    BIReport,
    SyncJob
)
from app.schemas.bi import (
    BIConnectionCreate, BIConnectionUpdate,
    BIDashboardCreate, BIDashboardUpdate,
    BIReportCreate, BIReportUpdate,
    SyncJobCreate, SyncJobUpdate
)
from app.core.exceptions import NotFoundException
import uuid

class BIService:
    """Service for managing BI connections, dashboards, reports, and sync jobs."""

    # Connection methods
    def get_connection(
        self, db: Session, *, id: uuid.UUID
    ) -> Optional[BIConnection]:
        """Get a BI connection by ID."""
        return bi_connection_repository.get(db, id=id)

    def get_connections_by_user(
        self, db: Session, *, user_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[BIConnection]:
        """Get BI connections by user."""
        return bi_connection_repository.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

    def get_connections_by_platform(
        self, db: Session, *, platform_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[BIConnection]:
        """Get BI connections by platform type."""
        return bi_connection_repository.get_by_platform_type(
            db, platform_type=platform_type, skip=skip, limit=limit
        )

    def create_connection(
        self, db: Session, *, obj_in: BIConnectionCreate
    ) -> BIConnection:
        """Create a new BI connection."""
        return bi_connection_repository.create(db, obj_in=obj_in)

    def update_connection(
        self, db: Session, *, id: uuid.UUID, obj_in: BIConnectionUpdate
    ) -> BIConnection:
        """Update a BI connection."""
        db_obj = bi_connection_repository.get(db, id=id)
        if not db_obj:
            raise NotFoundException(f"BI connection with id {id} not found")
        return bi_connection_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_connection(
        self, db: Session, *, id: uuid.UUID
    ) -> BIConnection:
        """Delete a BI connection."""
        return bi_connection_repository.delete(db, id=id)

    # Dashboard methods
    def get_dashboard(
        self, db: Session, *, id: uuid.UUID
    ) -> Optional[BIDashboard]:
        """Get a BI dashboard by ID."""
        return bi_dashboard_repository.get(db, id=id)

    def get_dashboards_by_connection(
        self, db: Session, *, connection_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[BIDashboard]:
        """Get dashboards by connection."""
        return bi_dashboard_repository.get_by_connection(
            db, connection_id=connection_id, skip=skip, limit=limit
        )

    def create_dashboard(
        self, db: Session, *, obj_in: BIDashboardCreate
    ) -> BIDashboard:
        """Create a new BI dashboard."""
        return bi_dashboard_repository.create(db, obj_in=obj_in)

    def update_dashboard(
        self, db: Session, *, id: uuid.UUID, obj_in: BIDashboardUpdate
    ) -> BIDashboard:
        """Update a BI dashboard."""
        db_obj = bi_dashboard_repository.get(db, id=id)
        if not db_obj:
            raise NotFoundException(f"BI dashboard with id {id} not found")
        return bi_dashboard_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_dashboard(
        self, db: Session, *, id: uuid.UUID
    ) -> BIDashboard:
        """Delete a BI dashboard."""
        return bi_dashboard_repository.delete(db, id=id)

    # Report methods
    def get_report(
        self, db: Session, *, id: uuid.UUID
    ) -> Optional[BIReport]:
        """Get a BI report by ID."""
        return bi_report_repository.get(db, id=id)

    def get_reports_by_dashboard(
        self, db: Session, *, dashboard_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[BIReport]:
        """Get reports by dashboard."""
        return bi_report_repository.get_by_dashboard(
            db, dashboard_id=dashboard_id, skip=skip, limit=limit
        )

    def create_report(
        self, db: Session, *, obj_in: BIReportCreate
    ) -> BIReport:
        """Create a new BI report."""
        return bi_report_repository.create(db, obj_in=obj_in)

    def update_report(
        self, db: Session, *, id: uuid.UUID, obj_in: BIReportUpdate
    ) -> BIReport:
        """Update a BI report."""
        db_obj = bi_report_repository.get(db, id=id)
        if not db_obj:
            raise NotFoundException(f"BI report with id {id} not found")
        return bi_report_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_report(
        self, db: Session, *, id: uuid.UUID
    ) -> BIReport:
        """Delete a BI report."""
        return bi_report_repository.delete(db, id=id)

    # Sync job methods
    def get_sync_job(
        self, db: Session, *, id: uuid.UUID
    ) -> Optional[SyncJob]:
        """Get a sync job by ID."""
        return sync_job_repository.get(db, id=id)

    def get_sync_jobs_by_connection(
        self, db: Session, *, connection_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[SyncJob]:
        """Get sync jobs by connection."""
        return sync_job_repository.get_by_connection(
            db, connection_id=connection_id, skip=skip, limit=limit
        )

    def get_sync_jobs_by_status(
        self, db: Session, *, status: str,
        skip: int = 0, limit: int = 100
    ) -> List[SyncJob]:
        """Get sync jobs by status."""
        return sync_job_repository.get_by_status(
            db, status=status, skip=skip, limit=limit
        )

    def create_sync_job(
        self, db: Session, *, obj_in: SyncJobCreate
    ) -> SyncJob:
        """Create a new sync job."""
        return sync_job_repository.create(db, obj_in=obj_in)

    def update_sync_job(
        self, db: Session, *, id: uuid.UUID, obj_in: SyncJobUpdate
    ) -> SyncJob:
        """Update a sync job."""
        db_obj = sync_job_repository.get(db, id=id)
        if not db_obj:
            raise NotFoundException(f"Sync job with id {id} not found")
        return sync_job_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_sync_job(
        self, db: Session, *, id: uuid.UUID
    ) -> SyncJob:
        """Delete a sync job."""
        return sync_job_repository.delete(db, id=id)

# Create service instance
bi_service = BIService() 