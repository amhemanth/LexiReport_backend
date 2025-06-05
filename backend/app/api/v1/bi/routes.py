from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.bi import BIConnectionCreate, BIConnectionResponse, BIDashboardResponse, BIReportResponse, SyncJobResponse
from app.services.bi import bi_service
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/connections", response_model=List[BIConnectionResponse])
def list_bi_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [BIConnectionResponse.from_orm(c) for c in bi_service.get_connections(db, current_user.id)]

@router.post("/connect", response_model=BIConnectionResponse)
def create_bi_connection(
    obj_in: BIConnectionCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return BIConnectionResponse.from_orm(bi_service.create_connection(db, current_user.id, obj_in))

@router.get("/dashboards", response_model=List[BIDashboardResponse])
def list_dashboards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Stub: Return example dashboards
    return [
        BIDashboardResponse(
            id=uuid.uuid4(),
            connection_id=uuid.uuid4(),
            name="Sales Dashboard",
            metadata={"widgets": 5},
            created_at=datetime.utcnow()
        )
    ]

@router.get("/reports", response_model=List[BIReportResponse])
def list_bi_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Stub: Return example reports
    return [
        BIReportResponse(
            id=uuid.uuid4(),
            dashboard_id=uuid.uuid4(),
            name="Monthly Sales Report",
            metadata={"rows": 100},
            created_at=datetime.utcnow()
        )
    ]

@router.post("/sync", response_model=SyncJobResponse)
def trigger_sync_job(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Stub: Return example sync job
    return SyncJobResponse(
        id=uuid.uuid4(),
        connection_id=uuid.uuid4(),
        status="completed",
        started_at=datetime.utcnow(),
        finished_at=datetime.utcnow(),
        details={"synced": True}
    ) 