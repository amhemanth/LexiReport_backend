from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.schemas.ai import (
    AIAnalysisCreate, AIAnalysisUpdate, AIAnalysisResponse,
    QuestionAnswerCreate, QuestionAnswerUpdate, QuestionAnswerResponse,
    InsightGenerationCreate, InsightGenerationUpdate, InsightGenerationResponse
)
from app.repositories.ai import (
    ai_analysis_repository,
    question_answer_repository,
    insight_generation_repository
)
from app.models.ai import AIAnalysis, QuestionAnswer, InsightGeneration

class AIService:
    """Service for AI-powered analysis and insight generation."""

    async def create_analysis(
        self,
        db: Session,
        analysis: AIAnalysisCreate
    ) -> AIAnalysisResponse:
        """Create a new AI analysis."""
        try:
            db_analysis = await ai_analysis_repository.create(db, obj_in=analysis)
            return AIAnalysisResponse.model_validate(db_analysis)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating analysis: {str(e)}"
            )

    async def get_analysis(
        self,
        db: Session,
        analysis_id: uuid.UUID
    ) -> AIAnalysisResponse:
        """Get an AI analysis by ID."""
        analysis = await ai_analysis_repository.get(db, id=analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return AIAnalysisResponse.model_validate(analysis)

    async def update_analysis(
        self,
        db: Session,
        analysis_id: uuid.UUID,
        analysis: AIAnalysisUpdate
    ) -> AIAnalysisResponse:
        """Update an AI analysis."""
        db_analysis = await ai_analysis_repository.get(db, id=analysis_id)
        if not db_analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        updated_analysis = await ai_analysis_repository.update(
            db, db_obj=db_analysis, obj_in=analysis
        )
        return AIAnalysisResponse.model_validate(updated_analysis)

    async def delete_analysis(
        self,
        db: Session,
        analysis_id: uuid.UUID
    ) -> None:
        """Delete an AI analysis."""
        db_analysis = await ai_analysis_repository.get(db, id=analysis_id)
        if not db_analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        await ai_analysis_repository.remove(db, id=analysis_id)

    async def create_question_answer(
        self,
        db: Session,
        qa: QuestionAnswerCreate
    ) -> QuestionAnswerResponse:
        """Create a new question-answer entry."""
        try:
            db_qa = await question_answer_repository.create(db, obj_in=qa)
            return QuestionAnswerResponse.model_validate(db_qa)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating Q&A: {str(e)}"
            )

    async def get_question_answer(
        self,
        db: Session,
        qa_id: uuid.UUID
    ) -> QuestionAnswerResponse:
        """Get a question-answer entry by ID."""
        qa = await question_answer_repository.get(db, id=qa_id)
        if not qa:
            raise HTTPException(status_code=404, detail="Q&A not found")
        return QuestionAnswerResponse.model_validate(qa)

    async def update_question_answer(
        self,
        db: Session,
        qa_id: uuid.UUID,
        qa: QuestionAnswerUpdate
    ) -> QuestionAnswerResponse:
        """Update a question-answer entry."""
        db_qa = await question_answer_repository.get(db, id=qa_id)
        if not db_qa:
            raise HTTPException(status_code=404, detail="Q&A not found")
        
        updated_qa = await question_answer_repository.update(
            db, db_obj=db_qa, obj_in=qa
        )
        return QuestionAnswerResponse.model_validate(updated_qa)

    async def delete_question_answer(
        self,
        db: Session,
        qa_id: uuid.UUID
    ) -> None:
        """Delete a question-answer entry."""
        db_qa = await question_answer_repository.get(db, id=qa_id)
        if not db_qa:
            raise HTTPException(status_code=404, detail="Q&A not found")
        
        await question_answer_repository.remove(db, id=qa_id)

    async def create_insight_generation(
        self,
        db: Session,
        insight: InsightGenerationCreate
    ) -> InsightGenerationResponse:
        """Create a new insight generation entry."""
        try:
            db_insight = await insight_generation_repository.create(db, obj_in=insight)
            return InsightGenerationResponse.model_validate(db_insight)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating insight: {str(e)}"
            )

    async def get_insight_generation(
        self,
        db: Session,
        insight_id: uuid.UUID
    ) -> InsightGenerationResponse:
        """Get an insight generation entry by ID."""
        insight = await insight_generation_repository.get(db, id=insight_id)
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        return InsightGenerationResponse.model_validate(insight)

    async def update_insight_generation(
        self,
        db: Session,
        insight_id: uuid.UUID,
        insight: InsightGenerationUpdate
    ) -> InsightGenerationResponse:
        """Update an insight generation entry."""
        db_insight = await insight_generation_repository.get(db, id=insight_id)
        if not db_insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        updated_insight = await insight_generation_repository.update(
            db, db_obj=db_insight, obj_in=insight
        )
        return InsightGenerationResponse.model_validate(updated_insight)

    async def delete_insight_generation(
        self,
        db: Session,
        insight_id: uuid.UUID
    ) -> None:
        """Delete an insight generation entry."""
        db_insight = await insight_generation_repository.get(db, id=insight_id)
        if not db_insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        await insight_generation_repository.remove(db, id=insight_id)

# Create service instance
ai_service = AIService() 