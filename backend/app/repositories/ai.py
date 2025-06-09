from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.reports.report_insight import ReportInsight
from app.models.reports.enums import AnalysisType
from app.schemas.ai import (
    AIAnalysisCreate, AIAnalysisUpdate,
    QuestionAnswerCreate, QuestionAnswerUpdate,
    InsightGenerationCreate, InsightGenerationUpdate
)
from app.repositories.base import BaseRepository
import uuid

class AIAnalysisRepository(BaseRepository[ReportInsight, AIAnalysisCreate, AIAnalysisUpdate]):
    """Repository for AI analysis operations."""
    
    def get_by_report(self, db: Session, report_id: uuid.UUID) -> List[ReportInsight]:
        """Get all analyses for a report."""
        return db.query(self.model).filter(self.model.report_id == report_id).all()
    
    def get_by_status(self, db: Session, status: str) -> List[ReportInsight]:
        """Get all analyses with a specific status."""
        return db.query(self.model).filter(self.model.status == status).all()
    
    def get_by_type(self, db: Session, analysis_type: str) -> List[ReportInsight]:
        """Get all analyses of a specific type."""
        return db.query(self.model).filter(self.model.analysis_type == analysis_type).all()

class QuestionAnswerRepository(BaseRepository[ReportInsight, QuestionAnswerCreate, QuestionAnswerUpdate]):
    """Repository for question answering operations."""
    
    def get_by_context(self, db: Session, context: str) -> List[ReportInsight]:
        """Get all Q&A entries for a specific context."""
        return db.query(self.model).filter(self.model.context == context).all()
    
    def get_by_confidence(self, db: Session, min_confidence: float) -> List[ReportInsight]:
        """Get all Q&A entries with confidence above threshold."""
        return db.query(self.model).filter(self.model.confidence >= min_confidence).all()

class InsightGenerationRepository(BaseRepository[ReportInsight, InsightGenerationCreate, InsightGenerationUpdate]):
    """Repository for insight generation operations."""
    
    def get_by_report(self, db: Session, report_id: uuid.UUID) -> List[ReportInsight]:
        """Get all insights for a report."""
        return db.query(self.model).filter(self.model.report_id == report_id).all()
    
    def get_by_type(self, db: Session, insight_type: str) -> List[ReportInsight]:
        """Get all insights of a specific type."""
        return db.query(self.model).filter(self.model.insight_type == insight_type).all()

# Create repository instances
ai_analysis_repository = AIAnalysisRepository(ReportInsight)
question_answer_repository = QuestionAnswerRepository(ReportInsight)
insight_generation_repository = InsightGenerationRepository(ReportInsight) 