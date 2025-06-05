from sqlalchemy.orm import Session
from app.models.report import Report, ReportType, ReportStatus, ReportVersion, ReportInsight, ReportShare
from app.schemas.report import ReportCreate, ReportUpdate
from typing import Optional, List
import uuid

class ReportRepository:
    def get(self, db: Session, report_id: uuid.UUID) -> Optional[Report]:
        return db.query(Report).filter(Report.id == report_id).first()

    def get_by_user(self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Report]:
        return db.query(Report).filter(Report.user_id == user_id).offset(skip).limit(limit).all()

    def create(self, db: Session, user_id: uuid.UUID, obj_in: ReportCreate, file_path: str, file_type: str, file_size: int) -> Report:
        db_obj = Report(
            user_id=user_id,
            title=obj_in.title,
            description=obj_in.description,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            report_type_id=obj_in.report_type_id,
            metadata=obj_in.metadata
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Report, obj_in: ReportUpdate) -> Report:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Report) -> None:
        db.delete(db_obj)
        db.commit()

    # Add similar CRUD/query methods for ReportType, ReportStatus, ReportVersion, ReportInsight, ReportShare as needed

report_repository = ReportRepository() 