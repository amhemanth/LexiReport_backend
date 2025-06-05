from sqlalchemy.orm import Session
from app.models.processing.offline import OfflineContent
from app.models.processing.document_processing import SyncQueue, ProcessingJob
from typing import List
import uuid

class OfflineContentRepository:
    def get_by_user(self, db: Session, user_id: uuid.UUID) -> List[OfflineContent]:
        return db.query(OfflineContent).filter(OfflineContent.user_id == user_id).all()

offline_content_repository = OfflineContentRepository()

class SyncQueueRepository:
    def get_all(self, db: Session) -> List[SyncQueue]:
        return db.query(SyncQueue).all()

sync_queue_repository = SyncQueueRepository()

class ProcessingJobRepository:
    def get_all(self, db: Session) -> List[ProcessingJob]:
        return db.query(ProcessingJob).all()

processing_job_repository = ProcessingJobRepository() 