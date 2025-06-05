from sqlalchemy.orm import Session
from app.models.reports import ReportInsight, ReportQuery
from app.schemas.insight import ReportInsightCreate, ReportInsightUpdate
from typing import Optional, List
import uuid

class ReportInsightRepository:
    def get_by_report(self, db: Session, report_id: uuid.UUID) -> List[ReportInsight]:
        return db.query(ReportInsight).filter(ReportInsight.report_id == report_id).all()

    def create(self, db: Session, report_id: uuid.UUID, obj_in: ReportInsightCreate) -> ReportInsight:
        db_obj = ReportInsight(report_id=report_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ReportInsight, obj_in: ReportInsightUpdate) -> ReportInsight:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: ReportInsight) -> None:
        db.delete(db_obj)
        db.commit()

class ReportQueryRepository:
    def get_by_report(self, db: Session, report_id: uuid.UUID) -> List[ReportQuery]:
        return db.query(ReportQuery).filter(ReportQuery.report_id == report_id).all()

    def create(self, db: Session, report_id: uuid.UUID, user_id: uuid.UUID, question: str, response_text: str = None, confidence_score: float = None) -> ReportQuery:
        db_obj = ReportQuery(report_id=report_id, user_id=user_id, query_text=question, response_text=response_text, confidence_score=confidence_score)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

report_insight_repository = ReportInsightRepository()
report_query_repository = ReportQueryRepository() 