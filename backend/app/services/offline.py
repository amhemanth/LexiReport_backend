from sqlalchemy.orm import Session
from app.repositories.offline import offline_content_repository, sync_queue_repository, processing_job_repository
from app.models.processing.offline import OfflineContent
from app.models.processing.document_processing import SyncQueue, ProcessingJob
from typing import List, Optional, Dict, Any
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProcessingJobError(Exception):
    """Base exception for processing job errors."""
    pass

class OfflineService:
    def get_offline_content(self, db: Session, user_id: uuid.UUID) -> List[OfflineContent]:
        """Get offline content for a user."""
        return offline_content_repository.get_by_user(db, user_id)

    def get_sync_queue(self, db: Session) -> List[SyncQueue]:
        """Get all sync queue entries."""
        return sync_queue_repository.get_all(db)

    def get_processing_jobs(self, db: Session) -> List[ProcessingJob]:
        """Get all processing jobs."""
        return processing_job_repository.get_all(db)

    def create_processing_job(
        self,
        db: Session,
        user_id: uuid.UUID,
        job_type: str,
        content_id: uuid.UUID,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ) -> ProcessingJob:
        """Create a new processing job."""
        try:
            job = ProcessingJob(
                user_id=user_id,
                job_type=job_type,
                content_id=content_id,
                parameters=parameters,
                priority=priority,
                status="pending",
                progress=0.0
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"Created processing job {job.id} of type {job_type}")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create processing job: {str(e)}")
            raise ProcessingJobError(f"Failed to create job: {str(e)}")

    def update_job_progress(
        self,
        db: Session,
        job_id: uuid.UUID,
        progress: float,
        status: Optional[str] = None
    ) -> ProcessingJob:
        """Update job progress and optionally status."""
        try:
            job = processing_job_repository.get(db, id=job_id)
            if not job:
                raise ProcessingJobError(f"Job {job_id} not found")

            job.progress = progress
            if status:
                job.status = status
            job.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(job)
            logger.info(f"Updated job {job_id} progress to {progress}")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update job progress: {str(e)}")
            raise ProcessingJobError(f"Failed to update progress: {str(e)}")

    def complete_job(
        self,
        db: Session,
        job_id: uuid.UUID,
        result: Dict[str, Any]
    ) -> ProcessingJob:
        """Mark a job as completed with results."""
        try:
            job = processing_job_repository.get(db, id=job_id)
            if not job:
                raise ProcessingJobError(f"Job {job_id} not found")

            job.status = "completed"
            job.progress = 1.0
            job.result = result
            job.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(job)
            logger.info(f"Completed job {job_id}")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to complete job: {str(e)}")
            raise ProcessingJobError(f"Failed to complete job: {str(e)}")

    def fail_job(
        self,
        db: Session,
        job_id: uuid.UUID,
        error: str
    ) -> ProcessingJob:
        """Mark a job as failed with error message."""
        try:
            job = processing_job_repository.get(db, id=job_id)
            if not job:
                raise ProcessingJobError(f"Job {job_id} not found")

            job.status = "failed"
            job.error = error
            job.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(job)
            logger.error(f"Failed job {job_id}: {error}")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to mark job as failed: {str(e)}")
            raise ProcessingJobError(f"Failed to mark job as failed: {str(e)}")

    def get_job_by_id(self, db: Session, job_id: uuid.UUID) -> Optional[ProcessingJob]:
        """Get a specific job by ID."""
        return processing_job_repository.get(db, id=job_id)

    def get_jobs_by_user(
        self,
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProcessingJob]:
        """Get all jobs for a specific user."""
        return processing_job_repository.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_jobs_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProcessingJob]:
        """Get all jobs with a specific status."""
        return processing_job_repository.get_multi_by_field(
            db, field="status", value=status, skip=skip, limit=limit
        )

offline_service = OfflineService() 