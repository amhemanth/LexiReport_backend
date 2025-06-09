from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from fastapi import HTTPException

from app.models.reports import Report, ReportInsight, ReportQuery
from app.models.core.user import User
from app.schemas.insight import (
    ReportInsightCreate, ReportInsightResponse, ReportInsightUpdate,
    ReportQueryCreate, ReportQueryResponse, InsightCreate, InsightUpdate, InsightResponse
)
from app.config.settings import get_settings
from app.repositories.insight import report_insight_repository, report_query_repository, insight_repository
from app.services.ai_service import AIService
from app.core.exceptions import NotFoundError, ValidationError

settings = get_settings()
ai_service = AIService()

class InsightService:
    """Service for handling report insights."""

    def __init__(self, db: Session):
        self.db = db
        self.cache_dir = settings.CACHE_DIR
        self.cache_ttl = settings.CACHE_TTL

    async def generate_insights(
        self,
        user: User,
        report_id: uuid.UUID,
        insight_types: Optional[List[str]] = None
    ) -> List[ReportInsightResponse]:
        """Generate insights for a report using AI."""
        # Get report
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.created_by == user.id)
            .first()
        )
        if not report:
            raise NotFoundError(f"Report {report_id} not found")

        # Default insight types if not specified
        if not insight_types:
            insight_types = ["summary", "key_points", "recommendations"]

        insights = []
        for insight_type in insight_types:
            # Generate insight using AI
            insight_content, confidence_score = await self._generate_insight(
                report.file_path,
                insight_type
            )

            # Create insight record
            insight = ReportInsight(
                report_id=report.id,
                user_id=user.id,
                insight_type=insight_type,
                content=insight_content,
                confidence_score=confidence_score,
                metadata={
                    "model": ai_settings.MODEL_PATH,
                    "generation_time": datetime.utcnow().isoformat()
                }
            )
            self.db.add(insight)
            insights.append(insight)

        self.db.commit()
        for insight in insights:
            self.db.refresh(insight)

        return [ReportInsightResponse.from_orm(insight) for insight in insights]

    async def get_insights(
        self,
        user: User,
        report_id: uuid.UUID,
        insight_type: Optional[str] = None,
        min_confidence: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[ReportInsightResponse]:
        """Get insights for a report with filtering and pagination."""
        # Verify report ownership
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.created_by == user.id)
            .first()
        )
        if not report:
            raise NotFoundError(f"Report {report_id} not found")

        # Build query
        query = self.db.query(ReportInsight).filter(ReportInsight.report_id == report_id)
        
        if insight_type:
            query = query.filter(ReportInsight.insight_type == insight_type)
        if min_confidence is not None:
            query = query.filter(ReportInsight.confidence_score >= min_confidence)
        if start_date:
            query = query.filter(ReportInsight.created_at >= start_date)
        if end_date:
            query = query.filter(ReportInsight.created_at <= end_date)

        # Apply sorting
        if hasattr(ReportInsight, sort_by):
            sort_column = getattr(ReportInsight, sort_by)
            query = query.order_by(desc(sort_column) if sort_desc else sort_column)

        # Apply pagination
        insights = query.offset(skip).limit(limit).all()
        return [ReportInsightResponse.from_orm(insight) for insight in insights]

    async def update_insight(
        self,
        user: User,
        insight_id: uuid.UUID,
        update_data: ReportInsightUpdate
    ) -> ReportInsightResponse:
        """Update an insight."""
        # Get insight and verify report ownership
        insight = (
            self.db.query(ReportInsight)
            .join(Report)
            .filter(
                ReportInsight.id == insight_id,
                Report.created_by == user.id
            )
            .first()
        )
        if not insight:
            raise NotFoundError(f"Insight {insight_id} not found")

        # Update insight
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(insight, field, value)
        
        insight.metadata["last_updated"] = datetime.utcnow().isoformat()

        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)

        return ReportInsightResponse.from_orm(insight)

    async def delete_insight(
        self,
        user: User,
        insight_id: uuid.UUID
    ) -> bool:
        """Delete an insight."""
        # Get insight and verify report ownership
        insight = (
            self.db.query(ReportInsight)
            .join(Report)
            .filter(
                ReportInsight.id == insight_id,
                Report.created_by == user.id
            )
            .first()
        )
        if not insight:
            raise NotFoundError(f"Insight {insight_id} not found")

        self.db.delete(insight)
        self.db.commit()

        return True

    async def bulk_create_insights(
        self,
        user: User,
        report_id: uuid.UUID,
        insights: List[ReportInsightCreate]
    ) -> List[ReportInsightResponse]:
        """Create multiple insights in bulk."""
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.created_by == user.id)
            .first()
        )
        if not report:
            raise NotFoundError(f"Report {report_id} not found")

        created_insights = []
        for insight_data in insights:
            insight = ReportInsight(
                report_id=report.id,
                user_id=user.id,
                **insight_data.dict()
            )
            self.db.add(insight)
            created_insights.append(insight)

        self.db.commit()
        for insight in created_insights:
            self.db.refresh(insight)

        return [ReportInsightResponse.from_orm(insight) for insight in created_insights]

    async def _generate_insight(
        self,
        file_path: str,
        insight_type: str
    ) -> Tuple[str, float]:
        """Generate an insight using AI."""
        try:
            # TODO: Implement actual AI integration
            # This is a placeholder that should be replaced with actual AI processing
            if insight_type == "summary":
                return "This is a summary of the report.", 0.95
            elif insight_type == "key_points":
                return "Key points from the report:\n1. Point 1\n2. Point 2", 0.90
            elif insight_type == "recommendations":
                return "Recommendations:\n1. Recommendation 1\n2. Recommendation 2", 0.85
            else:
                return "No insight available.", 0.0
        except Exception as e:
            raise ValidationError(f"Failed to generate insight: {str(e)}")

    async def ask_question(
        self,
        user: User,
        report_id: uuid.UUID,
        question: str
    ) -> ReportQueryResponse:
        """Ask a question about a report."""
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.created_by == user.id)
            .first()
        )
        if not report:
            raise NotFoundError(f"Report {report_id} not found")

        # Use AIService for Q&A
        context = report.content if report else ""
        answer = await ai_service.answer_question(context, question) if context else "No context available."
        
        query = ReportQuery(
            report_id=report.id,
            user_id=user.id,
            query_text=question,
            response_text=answer,
            confidence_score=1.0
        )
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)

        return ReportQueryResponse.from_orm(query)

    async def create_insight(
        self,
        insight: InsightCreate
    ) -> InsightResponse:
        """Create a new insight."""
        try:
            db_insight = await insight_repository.create(self.db, obj_in=insight)
            return InsightResponse.model_validate(db_insight)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating insight: {str(e)}"
            )

    async def get_insight(
        self,
        insight_id: uuid.UUID
    ) -> InsightResponse:
        """Get an insight by ID."""
        insight = await insight_repository.get(self.db, id=insight_id)
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        return InsightResponse.model_validate(insight)

    async def update_insight(
        self,
        insight_id: uuid.UUID,
        insight: InsightUpdate
    ) -> InsightResponse:
        """Update an insight."""
        db_insight = await insight_repository.get(self.db, id=insight_id)
        if not db_insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        updated_insight = await insight_repository.update(
            self.db, db_obj=db_insight, obj_in=insight
        )
        return InsightResponse.model_validate(updated_insight)

    async def delete_insight(
        self,
        insight_id: uuid.UUID
    ) -> None:
        """Delete an insight."""
        db_insight = await insight_repository.get(self.db, id=insight_id)
        if not db_insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        await insight_repository.remove(self.db, id=insight_id)

    async def get_insights_by_report(
        self,
        report_id: uuid.UUID
    ) -> List[InsightResponse]:
        """Get all insights for a report."""
        insights = await insight_repository.get_multi_by_report(self.db, report_id=report_id)
        return [InsightResponse.model_validate(insight) for insight in insights]

insight_service = InsightService() 