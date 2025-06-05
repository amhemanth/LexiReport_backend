from sqlalchemy.orm import Session
from app.models.integration.bi_integration import BIConnection, BIDashboard, BIReport, SyncJob
from app.schemas.bi import BIConnectionCreate
from typing import Optional, List
import uuid

class BIConnectionRepository:
    def get_by_user(self, db: Session, user_id: uuid.UUID) -> List[BIConnection]:
        return db.query(BIConnection).filter(BIConnection.user_id == user_id).all()

    def create(self, db: Session, user_id: uuid.UUID, obj_in: BIConnectionCreate) -> BIConnection:
        db_obj = BIConnection(user_id=user_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

bi_connection_repository = BIConnectionRepository() 