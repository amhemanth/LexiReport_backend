from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
from app.models.core.user import User
from app.schemas.ai import (
    AIAnalysisRequest, AIAnalysisResponse,
    QuestionAnswerRequest, QuestionAnswerResponse,
    InsightGenerationRequest, InsightGenerationResponse
)
from app.services.ai_service import AIService
from datetime import datetime

router = APIRouter()
ai_service = AIService()

@router.post("/analyze", response_model=AIAnalysisResponse)
@require_permissions([Permission.API_ACCESS])
async def analyze_content(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze content using AI."""
    try:
        result = await ai_service.process_report(request.report)
        return AIAnalysisResponse(
            insights=result,
            metadata={
                "model": "gpt-4",
                "generated_at": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/qa", response_model=QuestionAnswerResponse)
@require_permissions([Permission.API_ACCESS])
async def answer_question(
    request: QuestionAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Answer a question about the given context."""
    try:
        answer = await ai_service.answer_question(
            context=request.context,
            question=request.question
        )
        return QuestionAnswerResponse(
            answer=answer,
            confidence=0.8,  # TODO: Get actual confidence from model
            metadata={
                "model": "distilbert-base-cased-distilled-squad",
                "generated_at": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/insights", response_model=InsightGenerationResponse)
@require_permissions([Permission.API_ACCESS])
async def generate_insights(
    request: InsightGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate insights from content."""
    try:
        insights = await ai_service._generate_insights(
            content=request.content,
            report=request.report
        )
        return InsightGenerationResponse(
            insights=insights,
            metadata={
                "model": "gpt-4",
                "generated_at": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 