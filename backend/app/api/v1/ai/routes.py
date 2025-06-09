from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
from app.models.core.user import User
from app.schemas.ai import (
    AIAnalysisCreate, AIAnalysisUpdate, AIAnalysisResponse, AIAnalysisList,
    QuestionAnswerCreate, QuestionAnswerUpdate, QuestionAnswerResponse, QuestionAnswerList,
    InsightGenerationCreate, InsightGenerationUpdate, InsightGenerationResponse, InsightGenerationList
)
from app.services.ai_service import ai_service
from app.repositories.ai import (
    ai_analysis_repository,
    question_answer_repository,
    insight_generation_repository
)
import uuid

router = APIRouter()

# AI Analysis routes
@router.get("/analyses", response_model=AIAnalysisList)
@require_permissions([Permission.API_ACCESS])
async def list_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    report_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    analysis_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List AI analyses with optional filtering."""
    try:
        filters = {}
        if report_id:
            filters["report_id"] = report_id
        if status:
            filters["status"] = status
        if analysis_type:
            filters["analysis_type"] = analysis_type

        analyses = await ai_analysis_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters
        )
        total = await ai_analysis_repository.count(db, filters=filters)
        return AIAnalysisList(
            items=analyses,
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/analyses", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.API_ACCESS])
async def create_analysis(
    analysis: AIAnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI analysis."""
    return await ai_service.create_analysis(db, analysis)

@router.get("/analyses/{analysis_id}", response_model=AIAnalysisResponse)
@require_permissions([Permission.API_ACCESS])
async def get_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get an AI analysis by ID."""
    return await ai_service.get_analysis(db, analysis_id)

@router.put("/analyses/{analysis_id}", response_model=AIAnalysisResponse)
@require_permissions([Permission.API_ACCESS])
async def update_analysis(
    analysis_id: uuid.UUID,
    analysis: AIAnalysisUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an AI analysis."""
    return await ai_service.update_analysis(db, analysis_id, analysis)

@router.delete("/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.API_ACCESS])
async def delete_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an AI analysis."""
    await ai_service.delete_analysis(db, analysis_id)

# Question Answer routes
@router.get("/qa", response_model=QuestionAnswerList)
@require_permissions([Permission.API_ACCESS])
async def list_question_answers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    context: Optional[str] = None,
    min_confidence: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List question-answer entries with optional filtering."""
    try:
        filters = {}
        if context:
            filters["context"] = context
        if min_confidence is not None:
            filters["min_confidence"] = min_confidence

        qa_entries = await question_answer_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters
        )
        total = await question_answer_repository.count(db, filters=filters)
        return QuestionAnswerList(
            items=qa_entries,
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/qa", response_model=QuestionAnswerResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.API_ACCESS])
async def create_question_answer(
    qa: QuestionAnswerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new question-answer entry."""
    return await ai_service.create_question_answer(db, qa)

@router.get("/qa/{qa_id}", response_model=QuestionAnswerResponse)
@require_permissions([Permission.API_ACCESS])
async def get_question_answer(
    qa_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a question-answer entry by ID."""
    return await ai_service.get_question_answer(db, qa_id)

@router.put("/qa/{qa_id}", response_model=QuestionAnswerResponse)
@require_permissions([Permission.API_ACCESS])
async def update_question_answer(
    qa_id: uuid.UUID,
    qa: QuestionAnswerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a question-answer entry."""
    return await ai_service.update_question_answer(db, qa_id, qa)

@router.delete("/qa/{qa_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.API_ACCESS])
async def delete_question_answer(
    qa_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a question-answer entry."""
    await ai_service.delete_question_answer(db, qa_id)

# Insight Generation routes
@router.get("/insights", response_model=InsightGenerationList)
@require_permissions([Permission.API_ACCESS])
async def list_insights(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    report_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    insight_types: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List insight generation entries with optional filtering."""
    try:
        filters = {}
        if report_id:
            filters["report_id"] = report_id
        if status:
            filters["status"] = status
        if insight_types:
            filters["insight_types"] = insight_types

        insights = await insight_generation_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters
        )
        total = await insight_generation_repository.count(db, filters=filters)
        return InsightGenerationList(
            items=insights,
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/insights", response_model=InsightGenerationResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.API_ACCESS])
async def create_insight(
    insight: InsightGenerationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new insight generation entry."""
    return await ai_service.create_insight_generation(db, insight)

@router.get("/insights/{insight_id}", response_model=InsightGenerationResponse)
@require_permissions([Permission.API_ACCESS])
async def get_insight(
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get an insight generation entry by ID."""
    return await ai_service.get_insight_generation(db, insight_id)

@router.put("/insights/{insight_id}", response_model=InsightGenerationResponse)
@require_permissions([Permission.API_ACCESS])
async def update_insight(
    insight_id: uuid.UUID,
    insight: InsightGenerationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an insight generation entry."""
    return await ai_service.update_insight_generation(db, insight_id, insight)

@router.delete("/insights/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.API_ACCESS])
async def delete_insight(
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an insight generation entry."""
    await ai_service.delete_insight_generation(db, insight_id) 