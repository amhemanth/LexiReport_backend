from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.models.reports import ReportInsight, ReportQuery
from app.schemas.insight import (
    ReportInsightCreate, ReportInsightUpdate,
    ReportQueryCreate, ReportQueryUpdate,
    ReportQueryResponse
)
from .base import BaseRepository

class ReportInsightRepository(
    BaseRepository[ReportInsight, ReportInsightCreate, ReportInsightUpdate]
):
    """Repository for ReportInsight model."""

    def get_by_report(
        self, db: Session, *, report_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportInsight]:
        """Get insights by report."""
        return self.get_multi_by_field(
            db, field="report_id", value=report_id, skip=skip, limit=limit
        )

    def get_by_type(
        self, db: Session, *, insight_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[ReportInsight]:
        """Get insights by type."""
        return self.get_multi_by_field(
            db, field="insight_type", value=insight_type,
            skip=skip, limit=limit
        )

    def get_by_confidence(
        self, db: Session, *, min_confidence: float,
        skip: int = 0, limit: int = 100
    ) -> List[ReportInsight]:
        """Get insights by minimum confidence score."""
        return db.query(ReportInsight).filter(
            ReportInsight.confidence_score >= min_confidence
        ).offset(skip).limit(limit).all()

class ReportQueryRepository(
    BaseRepository[ReportQuery, ReportQueryCreate, ReportQueryUpdate]
):
    """Repository for ReportQuery model."""

    def get_by_report(
        self, db: Session, *, report_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportQuery]:
        """Get queries by report."""
        return self.get_multi_by_field(
            db, field="report_id", value=report_id, skip=skip, limit=limit
        )

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportQuery]:
        """Get queries by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_confidence(
        self, db: Session, *, min_confidence: float,
        skip: int = 0, limit: int = 100
    ) -> List[ReportQuery]:
        """Get queries by minimum confidence score."""
        return db.query(ReportQuery).filter(
            ReportQuery.confidence_score >= min_confidence
        ).offset(skip).limit(limit).all()

# Create repository instances
report_insight_repository = ReportInsightRepository(ReportInsight)
report_query_repository = ReportQueryRepository(ReportQuery) 