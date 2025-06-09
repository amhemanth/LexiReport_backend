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

class AIRequest(BaseModel):
    """Schema for AI processing requests."""
    text: str = Field(..., description="Text to process")
    model: Optional[str] = Field(None, description="Model to use for processing")
    temperature: Optional[float] = Field(None, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, description="Top p for nucleus sampling")
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(None, description="Presence penalty")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    timeout: Optional[int] = Field(None, description="Request timeout in seconds")
    retry_attempts: Optional[int] = Field(None, description="Number of retry attempts")
    retry_delay: Optional[int] = Field(None, description="Delay between retries in seconds")

class AIResponse(BaseModel):
    """Schema for AI processing responses."""
    id: uuid.UUID = Field(..., description="Response ID")
    text: str = Field(..., description="Generated text")
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(..., description="Creation timestamp")
    processing_time: float = Field(..., description="Processing time in seconds")
    tokens_used: int = Field(..., description="Number of tokens used")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class AIError(BaseModel):
    """Schema for AI processing errors."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

class AICacheEntry(BaseModel):
    """Schema for AI cache entries."""
    id: uuid.UUID = Field(..., description="Cache entry ID")
    request_hash: str = Field(..., description="Hash of the request")
    response: AIResponse = Field(..., description="Cached response")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    hits: int = Field(..., description="Number of cache hits")

class AIModelInfo(BaseModel):
    """Schema for AI model information."""
    name: str = Field(..., description="Model name")
    description: str = Field(..., description="Model description")
    version: str = Field(..., description="Model version")
    capabilities: List[str] = Field(..., description="Model capabilities")
    max_tokens: int = Field(..., description="Maximum tokens supported")
    is_available: bool = Field(..., description="Whether the model is available")
    last_updated: datetime = Field(..., description="Last update timestamp") 