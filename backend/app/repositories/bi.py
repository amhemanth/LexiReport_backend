from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.integration.bi_integration import BIConnection, BIDashboard, BIReport, SyncJob
from app.schemas.bi import (
    BIConnectionCreate, BIConnectionUpdate,
    BIDashboardCreate, BIDashboardUpdate,
    BIReportCreate, BIReportUpdate,
    SyncJobCreate, SyncJobUpdate
)
from .base import BaseRepository

class BIConnectionRepository(
    BaseRepository[BIConnection, BIConnectionCreate, BIConnectionUpdate]
):
    """Repository for BIConnection model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[BIConnection]:
        """Get BI connections by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_provider(
        self, db: Session, *, provider: str, skip: int = 0, limit: int = 100
    ) -> List[BIConnection]:
        """Get BI connections by provider."""
        return self.get_multi_by_field(
            db, field="provider", value=provider, skip=skip, limit=limit
        )

class BIDashboardRepository(
    BaseRepository[BIDashboard, BIDashboardCreate, BIDashboardUpdate]
):
    """Repository for BIDashboard model."""

    def get_by_connection(
        self, db: Session, *, connection_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[BIDashboard]:
        """Get dashboards by connection."""
        return self.get_multi_by_field(
            db, field="connection_id", value=connection_id,
            skip=skip, limit=limit
        )

class BIReportRepository(
    BaseRepository[BIReport, BIReportCreate, BIReportUpdate]
):
    """Repository for BIReport model."""

    def get_by_connection(
        self, db: Session, *, connection_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[BIReport]:
        """Get reports by connection."""
        return self.get_multi_by_field(
            db, field="connection_id", value=connection_id,
            skip=skip, limit=limit
        )

class SyncJobRepository(
    BaseRepository[SyncJob, SyncJobCreate, SyncJobUpdate]
):
    """Repository for SyncJob model."""

    def get_by_connection(
        self, db: Session, *, connection_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[SyncJob]:
        """Get sync jobs by connection."""
        return self.get_multi_by_field(
            db, field="connection_id", value=connection_id,
            skip=skip, limit=limit
        )

    def get_by_status(
        self, db: Session, *, status: str,
        skip: int = 0, limit: int = 100
    ) -> List[SyncJob]:
        """Get sync jobs by status."""
        return self.get_multi_by_field(
            db, field="status", value=status,
            skip=skip, limit=limit
        )

# Create repository instances
bi_connection_repository = BIConnectionRepository(BIConnection)
bi_dashboard_repository = BIDashboardRepository(BIDashboard)
bi_report_repository = BIReportRepository(BIReport)
sync_job_repository = SyncJobRepository(SyncJob) 