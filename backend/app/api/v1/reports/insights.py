from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.report import (
    ReportInsightResponse,
    ReportInsightCreate,
    ReportInsightUpdate
)
from app.services.report import ReportService
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/{report_id}/insights/generate")
async def generate_insights(
    report_id: int,
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
    report_id: int,
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
    report_id: int,
    insight_id: int,
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


@router.put("/{report_id}/insights/{insight_id}")
async def update_insight(
    report_id: int,
    insight_id: int,
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
    for field, value in update_data.items():
        setattr(insight, field, value)

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return ReportInsightResponse.from_orm(insight)


@router.delete("/{report_id}/insights/{insight_id}")
async def delete_insight(
    report_id: int,
    insight_id: int,
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