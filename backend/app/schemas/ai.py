from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.report import ReportBase

class AIAnalysisRequest(BaseModel):
    """Request for AI analysis."""
    report: ReportBase
    analysis_type: str = Field(..., description="Type of analysis to perform")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional analysis options")

class AIAnalysisResponse(BaseModel):
    """Response from AI analysis."""
    insights: List[Any]
    metadata: Dict[str, Any]

class QuestionAnswerRequest(BaseModel):
    """Request for question answering."""
    context: str = Field(..., description="Context to answer the question from")
    question: str = Field(..., description="Question to answer")

class QuestionAnswerResponse(BaseModel):
    """Response from question answering."""
    answer: str
    confidence: float
    metadata: Dict[str, Any]

class InsightGenerationRequest(BaseModel):
    """Request for insight generation."""
    content: str = Field(..., description="Content to generate insights from")
    report: ReportBase
    insight_types: Optional[List[str]] = Field(None, description="Types of insights to generate")

class InsightGenerationResponse(BaseModel):
    """Response from insight generation."""
    insights: List[Any]
    metadata: Dict[str, Any] 