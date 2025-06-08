from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .base import BaseSchema, TimestampSchema
from app.schemas.report import ReportBase
import uuid

class AIAnalysisBase(BaseSchema):
    """Base AI analysis schema."""
    analysis_type: str = Field(..., description="Type of analysis to perform")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional analysis options")
    status: str = Field(default="pending", description="Analysis status")

class AIAnalysisCreate(AIAnalysisBase):
    """Schema for AI analysis creation."""
    report_id: uuid.UUID

class AIAnalysisUpdate(BaseSchema):
    """Schema for AI analysis updates."""
    status: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None

class AIAnalysisInDB(AIAnalysisBase, TimestampSchema):
    """Schema for AI analysis in database."""
    id: uuid.UUID
    report_id: uuid.UUID
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AIAnalysisResponse(AIAnalysisInDB):
    """Schema for AI analysis response."""
    report: Optional[Dict[str, Any]] = None

class AIAnalysisList(BaseSchema):
    """Schema for paginated AI analysis list."""
    items: List[AIAnalysisResponse]
    total: int
    page: int
    size: int
    pages: int

class QuestionAnswerBase(BaseSchema):
    """Base question answering schema."""
    context: str = Field(..., description="Context to answer the question from")
    question: str = Field(..., description="Question to answer")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")

class QuestionAnswerCreate(QuestionAnswerBase):
    """Schema for question answering creation."""
    pass

class QuestionAnswerUpdate(BaseSchema):
    """Schema for question answering updates."""
    answer: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class QuestionAnswerInDB(QuestionAnswerBase, TimestampSchema):
    """Schema for question answering in database."""
    id: uuid.UUID
    answer: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class QuestionAnswerResponse(QuestionAnswerInDB):
    """Schema for question answering response."""
    pass

class QuestionAnswerList(BaseSchema):
    """Schema for paginated question answering list."""
    items: List[QuestionAnswerResponse]
    total: int
    page: int
    size: int
    pages: int

class InsightGenerationBase(BaseSchema):
    """Base insight generation schema."""
    content: str = Field(..., description="Content to generate insights from")
    insight_types: Optional[List[str]] = Field(None, description="Types of insights to generate")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")

class InsightGenerationCreate(InsightGenerationBase):
    """Schema for insight generation creation."""
    report_id: uuid.UUID

class InsightGenerationUpdate(BaseSchema):
    """Schema for insight generation updates."""
    insights: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class InsightGenerationInDB(InsightGenerationBase, TimestampSchema):
    """Schema for insight generation in database."""
    id: uuid.UUID
    report_id: uuid.UUID
    insights: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: str = "pending"
    error: Optional[str] = None

class InsightGenerationResponse(InsightGenerationInDB):
    """Schema for insight generation response."""
    report: Optional[Dict[str, Any]] = None

class InsightGenerationList(BaseSchema):
    """Schema for paginated insight generation list."""
    items: List[InsightGenerationResponse]
    total: int
    page: int
    size: int
    pages: int 