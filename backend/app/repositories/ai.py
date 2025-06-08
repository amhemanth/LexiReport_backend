from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.ai import AIAnalysis, QuestionAnswer, InsightGeneration
from app.schemas.ai import (
    AIAnalysisCreate, AIAnalysisUpdate,
    QuestionAnswerCreate, QuestionAnswerUpdate,
    InsightGenerationCreate, InsightGenerationUpdate
)
from app.repositories.base import BaseRepository
import uuid

class AIAnalysisRepository(BaseRepository[AIAnalysis, AIAnalysisCreate, AIAnalysisUpdate]):
    """Repository for AI analysis operations."""
    
    def get_by_report(self, db: Session, report_id: uuid.UUID) -> List[AIAnalysis]:
        """Get all analyses for a report."""
        return db.query(self.model).filter(self.model.report_id == report_id).all()
    
    def get_by_status(self, db: Session, status: str) -> List[AIAnalysis]:
        """Get all analyses with a specific status."""
        return db.query(self.model).filter(self.model.status == status).all()
    
    def get_by_type(self, db: Session, analysis_type: str) -> List[AIAnalysis]:
        """Get all analyses of a specific type."""
        return db.query(self.model).filter(self.model.analysis_type == analysis_type).all()

class QuestionAnswerRepository(BaseRepository[QuestionAnswer, QuestionAnswerCreate, QuestionAnswerUpdate]):
    """Repository for question answering operations."""
    
    def get_by_context(self, db: Session, context: str) -> List[QuestionAnswer]:
        """Get all Q&A entries for a specific context."""
        return db.query(self.model).filter(self.model.context == context).all()
    
    def get_by_confidence(self, db: Session, min_confidence: float) -> List[QuestionAnswer]:
        """Get all Q&A entries with confidence above threshold."""
        return db.query(self.model).filter(self.model.confidence >= min_confidence).all()

class InsightGenerationRepository(BaseRepository[InsightGeneration, InsightGenerationCreate, InsightGenerationUpdate]):
    """Repository for insight generation operations."""
    
    def get_by_report(self, db: Session, report_id: uuid.UUID) -> List[InsightGeneration]:
        """Get all insights for a report."""
        return db.query(self.model).filter(self.model.report_id == report_id).all()
    
    def get_by_status(self, db: Session, status: str) -> List[InsightGeneration]:
        """Get all insights with a specific status."""
        return db.query(self.model).filter(self.model.status == status).all()
    
    def get_by_type(self, db: Session, insight_types: List[str]) -> List[InsightGeneration]:
        """Get all insights of specific types."""
        return db.query(self.model).filter(self.model.insight_types.overlap(insight_types)).all()

# Create repository instances
ai_analysis_repository = AIAnalysisRepository(AIAnalysis)
question_answer_repository = QuestionAnswerRepository(QuestionAnswer)
insight_generation_repository = InsightGenerationRepository(InsightGeneration) 