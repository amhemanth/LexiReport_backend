from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
import uuid

class ReportInsightCreate(BaseModel):
    insight_type: str
    content: str
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ReportInsightUpdate(BaseModel):
    content: Optional[str] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ReportInsightResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    user_id: uuid.UUID
    insight_type: str
    content: str
    confidence_score: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ReportQueryCreate(BaseModel):
    question: str

class ReportQueryUpdate(BaseModel):
    response_text: Optional[str] = None
    confidence_score: Optional[float] = None

class ReportQueryResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    user_id: uuid.UUID
    query_text: str
    response_text: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 