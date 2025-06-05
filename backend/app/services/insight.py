from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.models.report import Report, ReportInsight, ReportQuery
from app.models.user import User
from app.schemas.report import ReportInsightCreate, ReportInsightResponse, ReportQueryCreate
from app.config.ai_settings import get_ai_settings
from app.repositories.insight import report_insight_repository, report_query_repository

ai_settings = get_ai_settings()


class InsightService:
    """Service for handling report insights."""

    def __init__(self, db: Session):
        self.db = db

    async def generate_insights(
        self,
        user: User,
        report_id: int,
        insight_types: List[str] = None
    ) -> List[ReportInsightResponse]:
        """Generate insights for a report using AI."""
        # Get report
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user.id)
            .first()
        )
        if not report:
            return []

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
        report_id: int,
        insight_type: Optional[str] = None
    ) -> List[ReportInsightResponse]:
        """Get insights for a report."""
        # Verify report ownership
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user.id)
            .first()
        )
        if not report:
            return []

        # Query insights
        query = self.db.query(ReportInsight).filter(ReportInsight.report_id == report_id)
        if insight_type:
            query = query.filter(ReportInsight.insight_type == insight_type)
        
        insights = query.all()
        return [ReportInsightResponse.from_orm(insight) for insight in insights]

    async def update_insight(
        self,
        user: User,
        insight_id: int,
        content: str,
        confidence_score: float
    ) -> Optional[ReportInsightResponse]:
        """Update an insight."""
        # Get insight and verify report ownership
        insight = (
            self.db.query(ReportInsight)
            .join(Report)
            .filter(
                ReportInsight.id == insight_id,
                Report.user_id == user.id
            )
            .first()
        )
        if not insight:
            return None

        # Update insight
        insight.content = content
        insight.confidence_score = confidence_score
        insight.metadata["last_updated"] = datetime.utcnow().isoformat()

        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)

        return ReportInsightResponse.from_orm(insight)

    async def delete_insight(
        self,
        user: User,
        insight_id: int
    ) -> bool:
        """Delete an insight."""
        # Get insight and verify report ownership
        insight = (
            self.db.query(ReportInsight)
            .join(Report)
            .filter(
                ReportInsight.id == insight_id,
                Report.user_id == user.id
            )
            .first()
        )
        if not insight:
            return False

        self.db.delete(insight)
        self.db.commit()

        return True

    async def _generate_insight(
        self,
        file_path: str,
        insight_type: str
    ) -> tuple[str, float]:
        """Generate an insight using AI."""
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

    def get_insights(self, db: Session, report_id: uuid.UUID) -> List[ReportInsight]:
        return report_insight_repository.get_by_report(db, report_id)

    def create_insight(self, db: Session, report_id: uuid.UUID, obj_in: ReportInsightCreate) -> ReportInsight:
        return report_insight_repository.create(db, report_id, obj_in)

    def update_insight(self, db: Session, insight_id: uuid.UUID, obj_in: ReportInsightUpdate) -> Optional[ReportInsight]:
        insight = db.query(ReportInsight).filter(ReportInsight.id == insight_id).first()
        if not insight:
            return None
        return report_insight_repository.update(db, insight, obj_in)

    def delete_insight(self, db: Session, insight_id: uuid.UUID) -> None:
        insight = db.query(ReportInsight).filter(ReportInsight.id == insight_id).first()
        if insight:
            report_insight_repository.delete(db, insight)

    def ask_question(self, db: Session, report_id: uuid.UUID, user_id: uuid.UUID, question: str) -> ReportQuery:
        # Stub: Replace with actual AI/ML Q&A logic
        answer = f"Stub answer for: {question}"
        return report_query_repository.create(db, report_id, user_id, question, response_text=answer, confidence_score=1.0)

insight_service = InsightService() 