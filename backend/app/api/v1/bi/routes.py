from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.bi import BIConnectionCreate, BIConnectionResponse
from app.services.bi import bi_service
import uuid

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