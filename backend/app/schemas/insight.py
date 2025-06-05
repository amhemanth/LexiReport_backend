from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
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
    insight_type: str
    content: str
    confidence_score: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    class Config:
        orm_mode = True

class ReportQueryCreate(BaseModel):
    question: str

class ReportQueryResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    user_id: uuid.UUID
    query_text: str
    response_text: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime
    class Config:
        orm_mode = True 