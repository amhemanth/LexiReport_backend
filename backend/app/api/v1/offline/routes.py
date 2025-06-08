from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.schemas.offline import (
    OfflineContentResponse,
    SyncQueueResponse,
    ProcessingJobResponse,
    ProcessingJobCreate
)
from app.services.offline import offline_service
import uuid

router = APIRouter()

@router.get("/content", response_model=List[OfflineContentResponse])
def list_offline_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List offline content for the current user."""
    return [OfflineContentResponse.from_orm(c) for c in offline_service.get_offline_content(db, current_user.id)]

@router.get("/sync-queue", response_model=List[SyncQueueResponse])
def list_sync_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List sync queue entries."""
    return [SyncQueueResponse.from_orm(q) for q in offline_service.get_sync_queue(db)]

@router.get("/processing-jobs", response_model=List[ProcessingJobResponse])
def list_processing_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List processing jobs, optionally filtered by status."""
    if status:
        jobs = offline_service.get_jobs_by_status(db, status, skip, limit)
    else:
        jobs = offline_service.get_processing_jobs(db)
    return [ProcessingJobResponse.from_orm(j) for j in jobs]

@router.get("/processing-jobs/{job_id}", response_model=ProcessingJobResponse)
def get_processing_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific processing job."""
    job = offline_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found"
        )
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )
    return ProcessingJobResponse.from_orm(job)

@router.post("/processing-jobs", response_model=ProcessingJobResponse)
def create_processing_job(
    job_in: ProcessingJobCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new processing job."""
    try:
        job = offline_service.create_processing_job(
            db=db,
            user_id=current_user.id,
            job_type=job_in.job_type,
            content_id=job_in.content_id,
            parameters=job_in.parameters,
            priority=job_in.priority
        )
        return ProcessingJobResponse.from_orm(job)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/processing-jobs/user/me", response_model=List[ProcessingJobResponse])
def list_user_processing_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List processing jobs for the current user."""
    jobs = offline_service.get_jobs_by_user(db, current_user.id, skip, limit)
    return [ProcessingJobResponse.from_orm(j) for j in jobs] 