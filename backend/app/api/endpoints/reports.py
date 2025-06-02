from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
from pathlib import Path
import shutil

from app.core.database import get_db
from app.models.report import Report, ReportInsight, ReportType
from app.services.report_processor import ReportProcessor
from app.schemas.report import ReportCreate, Report as ReportSchema, ReportInsight as ReportInsightSchema
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()
report_processor = ReportProcessor()

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/reports/", response_model=ReportSchema)
async def create_report(
    title: str,
    description: str = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a new report."""
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ['pdf', 'xlsx', 'xls']:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Determine report type
    report_type = ReportType.PDF if file_ext == 'pdf' else ReportType.EXCEL
    
    # Process report and extract insights
    try:
        insights = report_processor.process_report(str(file_path), report_type.value)
        
        # Create report record
        db_report = Report(
            title=title,
            description=description,
            file_path=str(file_path),
            report_type=report_type,
            user_id=current_user.id
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        # Save insights
        for insight in insights:
            db_insight = ReportInsight(
                content=insight["content"],
                insight_metadata=insight["insight_metadata"],
                report_id=db_report.id
            )
            db.add(db_insight)
        
        db.commit()
        
        return {
            "id": db_report.id,
            "title": db_report.title,
            "description": db_report.description,
            "report_type": db_report.report_type,
            "insights": [
                {
                    "id": insight.id,
                    "content": insight.content,
                    "metadata": insight.insight_metadata
                }
                for insight in db_report.insights
            ]
        }
    
    except Exception as e:
        # Clean up on error
        db.delete(db_report)
        db.commit()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{report_id}", response_model=ReportSchema)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific report with its insights."""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": report.id,
        "title": report.title,
        "description": report.description,
        "report_type": report.report_type,
        "insights": [
            {
                "id": insight.id,
                "content": insight.content,
                "metadata": insight.insight_metadata
            }
            for insight in report.insights
        ]
    }

@router.get("/reports/", response_model=List[ReportSchema])
def list_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all reports."""
    reports = db.query(Report).filter(Report.user_id == current_user.id).offset(skip).limit(limit).all()
    return [
        {
            "id": report.id,
            "title": report.title,
            "description": report.description,
            "report_type": report.report_type,
            "insights": [
                {
                    "id": insight.id,
                    "content": insight.content,
                    "metadata": insight.insight_metadata
                }
                for insight in report.insights
            ]
        }
        for report in reports
    ]

@router.delete("/reports/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Delete the file
    try:
        os.remove(report.file_path)
    except OSError:
        pass  # Ignore if file doesn't exist
    
    # Delete the report and its insights
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"} 