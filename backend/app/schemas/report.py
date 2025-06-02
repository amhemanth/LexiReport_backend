from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.report import ReportType

class ReportInsightBase(BaseModel):
    content: str
    insight_metadata: Dict[str, Any]

class ReportInsightCreate(ReportInsightBase):
    pass

class ReportInsight(ReportInsightBase):
    id: int
    report_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: str
    report_type: str

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    user_id: int
    created_at: datetime
    insights: List[ReportInsight] = []

    class Config:
        from_attributes = True 