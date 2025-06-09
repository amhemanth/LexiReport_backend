from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.models.integration.bi_integration import BIConnection, BIDashboard, BISyncJob, BIIntegration
from app.schemas.bi import (
    BIConnectionCreate, BIConnectionUpdate,
    BIDashboardCreate, BIDashboardUpdate,
    BIIntegrationCreate, BIIntegrationUpdate,
    SyncJobCreate, SyncJobUpdate
)
from .base import BaseRepository

class BIConnectionRepository(
    BaseRepository[BIConnection, BIConnectionCreate, BIConnectionUpdate]
):
    """Repository for BIConnection model."""

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[BIConnection]:
        """Get BI connections by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_platform_type(
        self, db: Session, *, platform_type: str, skip: int = 0, limit: int = 100
    ) -> List[BIConnection]:
        """Get BI connections by platform type."""
        return self.get_multi_by_field(
            db, field="platform_type", value=platform_type, skip=skip, limit=limit
        )

class BIDashboardRepository(
    BaseRepository[BIDashboard, BIDashboardCreate, BIDashboardUpdate]
):
    """Repository for BIDashboard model."""

    def get_by_connection(
        self, db: Session, *, connection_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[BIDashboard]:
        """Get dashboards by connection."""
        return self.get_multi_by_field(
            db, field="connection_id", value=connection_id,
            skip=skip, limit=limit
        )

    def get_by_name(
        self, db: Session, *, name: str,
        skip: int = 0, limit: int = 100
    ) -> List[BIDashboard]:
        """Get dashboards by name."""
        return self.get_multi_by_field(
            db, field="name", value=name,
            skip=skip, limit=limit
        )

class SyncJobRepository(
    BaseRepository[BISyncJob, SyncJobCreate, SyncJobUpdate]
):
    """Repository for BISyncJob model."""

    def get_by_integration(
        self, db: Session, *, integration_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[BISyncJob]:
        """Get sync jobs by integration."""
        return self.get_multi_by_field(
            db, field="integration_id", value=integration_id,
            skip=skip, limit=limit
        )

    def get_by_status(
        self, db: Session, *, status: str,
        skip: int = 0, limit: int = 100
    ) -> List[BISyncJob]:
        """Get sync jobs by status."""
        return self.get_multi_by_field(
            db, field="sync_status", value=status,
            skip=skip, limit=limit
        )

class BIIntegrationRepository(
    BaseRepository[BIIntegration, BIIntegrationCreate, BIIntegrationUpdate]
):
    """Repository for BIIntegration model."""

    def get_by_platform_type(
        self, db: Session, *, platform_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[BIIntegration]:
        """Get integrations by platform type."""
        return self.get_multi_by_field(
            db, field="platform_type", value=platform_type,
            skip=skip, limit=limit
        )

    def get_by_entity(
        self, db: Session, *, entity_type: str, entity_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[BIIntegration]:
        """Get integrations by entity."""
        return self.get_multi_by_field(
            db, field="entity_type", value=entity_type,
            skip=skip, limit=limit
        )

# Create repository instances
bi_connection_repository = BIConnectionRepository(BIConnection)
bi_dashboard_repository = BIDashboardRepository(BIDashboard)
bi_integration_repository = BIIntegrationRepository(BIIntegration)
sync_job_repository = SyncJobRepository(BISyncJob) 