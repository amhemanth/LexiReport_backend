from sqlalchemy.orm import Session
from app.repositories.offline import offline_content_repository, sync_queue_repository, processing_job_repository
from app.models.processing.offline import OfflineContent
from app.models.processing.document_processing import SyncQueue, ProcessingJob
from typing import List
import uuid

class OfflineService:
    def get_offline_content(self, db: Session, user_id: uuid.UUID) -> List[OfflineContent]:
        return offline_content_repository.get_by_user(db, user_id)

    def get_sync_queue(self, db: Session) -> List[SyncQueue]:
        return sync_queue_repository.get_all(db)

    def get_processing_jobs(self, db: Session) -> List[ProcessingJob]:
        return processing_job_repository.get_all(db)

offline_service = OfflineService() 