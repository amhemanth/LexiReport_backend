import logging
from sqlalchemy.orm import Session

from app.models.report import ReportType, ReportStatus
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.config.settings import get_settings
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)
settings = get_settings()


def init_db(db: Session) -> None:
    """Initialize database with required data."""
    try:
        # Create initial report types if they don't exist
        report_types = [
            ReportType(
                name="Financial Report",
                description="Financial statements and analysis",
                supported_formats=["pdf", "xlsx", "docx"]
            ),
            ReportType(
                name="Performance Report",
                description="Performance metrics and KPIs",
                supported_formats=["pdf", "xlsx"]
            ),
            ReportType(
                name="Research Report",
                description="Research findings and analysis",
                supported_formats=["pdf", "docx"]
            ),
            ReportType(
                name="Analytics Report",
                description="Data analytics and insights",
                supported_formats=["pdf", "xlsx", "csv"]
            )
        ]

        for report_type in report_types:
            existing_type = db.query(ReportType).filter(ReportType.name == report_type.name).first()
            if not existing_type:
                db.add(report_type)

        # Create initial report statuses if they don't exist
        report_statuses = [
            ReportStatus(
                name="uploaded",
                description="Report has been uploaded"
            ),
            ReportStatus(
                name="processing",
                description="Report is being processed"
            ),
            ReportStatus(
                name="analyzed",
                description="Report has been analyzed"
            ),
            ReportStatus(
                name="voice_generated",
                description="Voice-over has been generated"
            ),
            ReportStatus(
                name="error",
                description="Error occurred during processing"
            )
        ]

        for status in report_statuses:
            existing_status = db.query(ReportStatus).filter(ReportStatus.name == status.name).first()
            if not existing_status:
                db.add(status)

        db.commit()
        logger.info("Initial data created successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating initial data: {e}")
        raise 