import logging
from sqlalchemy.orm import Session

from app.models.report import ReportType, ReportStatus
from app.models.core.user import User
from app.models.core.user_preferences import UserPreferences
from app.config.settings import get_settings
from app.core.security import get_password_hash
from app.repositories.user import user_repository
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)
settings = get_settings()


def init_db(db: Session) -> None:
    """Initialize the database with initial data."""
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

        # Create superuser if it doesn't exist
        user = user_repository.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name=settings.FIRST_SUPERUSER_FULL_NAME,
                is_superuser=True,
            )
            user = user_repository.create(db, obj_in=user_in)
            print(f"Created superuser {user.email}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating initial data: {e}")
        raise 