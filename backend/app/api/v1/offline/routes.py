from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.offline import OfflineContentResponse, SyncQueueResponse, ProcessingJobResponse
from app.services.offline import offline_service
import uuid

router = APIRouter()

@router.get("/content", response_model=List[OfflineContentResponse])
def list_offline_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [OfflineContentResponse.from_orm(c) for c in offline_service.get_offline_content(db, current_user.id)]

@router.get("/sync-queue", response_model=List[SyncQueueResponse])
def list_sync_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [SyncQueueResponse.from_orm(q) for q in offline_service.get_sync_queue(db)]

@router.get("/processing-jobs", response_model=List[ProcessingJobResponse])
def list_processing_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [ProcessingJobResponse.from_orm(j) for j in offline_service.get_processing_jobs(db)] 