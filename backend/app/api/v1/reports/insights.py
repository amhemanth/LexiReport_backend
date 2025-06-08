from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import uuid

from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.models.reports import ReportInsight
from app.schemas.insight import (
    ReportInsightResponse,
    ReportQueryCreate,
    ReportInsightUpdate,
    ReportInsightCreate
)
from app.services.report import ReportService
from app.services.ai_service import AIService
from app.repositories.report import report_repository

router = APIRouter()


@router.post("/{report_id}/insights/generate")
async def generate_insights(
    report_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate insights for a report."""
    report_service = ReportService(db)
    report = await report_service.get_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    ai_service = AIService()
    background_tasks.add_task(ai_service.process_report, report)
    
    return {"message": "Insight generation started"}


@router.get("/{report_id}/insights")
async def get_insights(
    report_id: uuid.UUID,
    insight_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ReportInsightResponse]:
    """Get insights for a report."""
    report_service = ReportService(db)
    report = await report_service.get_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    query = db.query(ReportInsight).filter(ReportInsight.report_id == report_id)
    if insight_type:
        query = query.filter(ReportInsight.insight_type == insight_type)
    
    insights = query.all()
    return [ReportInsightResponse.from_orm(insight) for insight in insights]


@router.get("/{report_id}/insights/{insight_id}")
async def get_insight(
    report_id: uuid.UUID,
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ReportInsightResponse:
    """Get a specific insight."""
    report_service = ReportService(db)
    report = await report_service.get_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    insight = (
        db.query(ReportInsight)
        .filter(
            ReportInsight.id == insight_id,
            ReportInsight.report_id == report_id
        )
        .first()
    )
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    return ReportInsightResponse.from_orm(insight)


@router.post("/{report_id}/insights")
async def create_insight(
    report_id: uuid.UUID,
    insight_in: ReportInsightCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ReportInsightResponse:
    """Create a new insight."""
    report_service = ReportService(db)
    report = await report_service.get_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    insight_data = insight_in.dict()
    insight_data["report_id"] = report_id
    insight_data["created_by"] = current_user.id
    insight_data["updated_by"] = current_user.id

    insight = ReportInsight(**insight_data)
    db.add(insight)
    db.commit()
    db.refresh(insight)

    return ReportInsightResponse.from_orm(insight)


@router.put("/{report_id}/insights/{insight_id}")
async def update_insight(
    report_id: uuid.UUID,
    insight_id: uuid.UUID,
    insight_in: ReportInsightUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ReportInsightResponse:
    """Update an insight."""
    report_service = ReportService(db)
    report = await report_service.get_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    insight = (
        db.query(ReportInsight)
        .filter(
            ReportInsight.id == insight_id,
            ReportInsight.report_id == report_id
        )
        .first()
    )
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    update_data = insight_in.dict(exclude_unset=True)
    update_data["updated_by"] = current_user.id
    
    for field, value in update_data.items():
        setattr(insight, field, value)

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return ReportInsightResponse.from_orm(insight)


@router.delete("/{report_id}/insights/{insight_id}")
async def delete_insight(
    report_id: uuid.UUID,
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an insight."""
    report_service = ReportService(db)
    report = await report_service.get_report(current_user, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    insight = (
        db.query(ReportInsight)
        .filter(
            ReportInsight.id == insight_id,
            ReportInsight.report_id == report_id
        )
        .first()
    )
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    db.delete(insight)
    db.commit()

    return {"message": "Insight deleted successfully"} 