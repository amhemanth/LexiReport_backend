from sqlalchemy.orm import Session
from app.repositories.bi import bi_connection_repository
from app.models.integration.bi_integration import BIConnection
from app.schemas.bi import BIConnectionCreate
from typing import List
import uuid

class BIService:
    def get_connections(self, db: Session, user_id: uuid.UUID) -> List[BIConnection]:
        return bi_connection_repository.get_by_user(db, user_id)

    def create_connection(self, db: Session, user_id: uuid.UUID, obj_in: BIConnectionCreate) -> BIConnection:
        return bi_connection_repository.create(db, user_id, obj_in)

bi_service = BIService() 