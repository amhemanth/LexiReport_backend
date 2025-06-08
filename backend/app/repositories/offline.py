from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.processing.offline import OfflineContent
from app.models.processing.document_processing import SyncQueue, ProcessingJob
from app.schemas.offline import (
    OfflineContentCreate, OfflineContentUpdate,
    SyncQueueCreate, SyncQueueUpdate,
    ProcessingJobCreate, ProcessingJobUpdate
)
from .base import BaseRepository

class OfflineContentRepository(
    BaseRepository[OfflineContent, OfflineContentCreate, OfflineContentUpdate]
):
    """Repository for OfflineContent model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[OfflineContent]:
        """Get offline content by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[OfflineContent]:
        """Get offline content by status."""
        return self.get_multi_by_field(
            db, field="status", value=status, skip=skip, limit=limit
        )

class SyncQueueRepository(
    BaseRepository[SyncQueue, SyncQueueCreate, SyncQueueUpdate]
):
    """Repository for SyncQueue model."""

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[SyncQueue]:
        """Get sync queue entries by status."""
        return self.get_multi_by_field(
            db, field="status", value=status, skip=skip, limit=limit
        )

    def get_by_priority(
        self, db: Session, *, priority: int, skip: int = 0, limit: int = 100
    ) -> List[SyncQueue]:
        """Get sync queue entries by priority."""
        return self.get_multi_by_field(
            db, field="priority", value=priority, skip=skip, limit=limit
        )

class ProcessingJobRepository(
    BaseRepository[ProcessingJob, ProcessingJobCreate, ProcessingJobUpdate]
):
    """Repository for ProcessingJob model."""

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[ProcessingJob]:
        """Get processing jobs by status."""
        return self.get_multi_by_field(
            db, field="status", value=status, skip=skip, limit=limit
        )

    def get_by_type(
        self, db: Session, *, job_type: str, skip: int = 0, limit: int = 100
    ) -> List[ProcessingJob]:
        """Get processing jobs by type."""
        return self.get_multi_by_field(
            db, field="job_type", value=job_type, skip=skip, limit=limit
        )

# Create repository instances
offline_content_repository = OfflineContentRepository(OfflineContent)
sync_queue_repository = SyncQueueRepository(SyncQueue)
processing_job_repository = ProcessingJobRepository(ProcessingJob) 