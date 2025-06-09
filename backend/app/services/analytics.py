from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.analytics import voice_command_repository
from app.models.analytics.voice_command import VoiceCommand
from app.schemas.analytics import (
    VoiceCommandCreate,
    VoiceCommandUpdate,
    VoiceCommandFilter,
    VoiceCommandResponse
)
from app.core.exceptions import NotFoundException
from datetime import datetime, timedelta
import logging

from app.repositories.analytics import analytics_repository

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for managing analytics and voice commands."""

    def get_voice_command(
        self, db: Session, *, id: str
    ) -> Optional[VoiceCommand]:
        """Get a voice command by ID."""
        return voice_command_repository.get(db, id=id)

    def get_voice_commands_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by user."""
        return voice_command_repository.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

    def get_voice_commands_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by entity."""
        return voice_command_repository.get_by_entity(
            db, entity_type=entity_type, entity_id=entity_id,
            skip=skip, limit=limit
        )

    def get_voice_commands_by_action_type(
        self, db: Session, *, action_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by action type."""
        return voice_command_repository.get_by_action_type(
            db, action_type=action_type, skip=skip, limit=limit
        )

    def get_voice_commands_by_status(
        self, db: Session, *, status: str,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by status."""
        return voice_command_repository.get_by_status(
            db, status=status, skip=skip, limit=limit
        )

    def create_voice_command(
        self, db: Session, *, obj_in: VoiceCommandCreate
    ) -> VoiceCommand:
        """Create a new voice command."""
        return voice_command_repository.create(db, obj_in=obj_in)

    def update_voice_command(
        self, db: Session, *, id: str, obj_in: VoiceCommandUpdate
    ) -> VoiceCommand:
        """Update a voice command."""
        db_obj = voice_command_repository.get(db, id=id)
        if not db_obj:
            raise NotFoundException(f"Voice command with id {id} not found")
        return voice_command_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_voice_command(
        self, db: Session, *, id: str
    ) -> VoiceCommand:
        """Delete a voice command."""
        return voice_command_repository.delete(db, id=id)

    def filter_voice_commands(
        self, db: Session, *, filter_obj: VoiceCommandFilter,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Filter voice commands based on criteria."""
        return voice_command_repository.filter(
            db, filter_obj=filter_obj, skip=skip, limit=limit
        )

    def get_dashboard_analytics(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get dashboard analytics for the specified time range."""
        try:
            return analytics_repository.get_dashboard_analytics(
                db, start_date=start_date, end_date=end_date
            )
        except Exception as e:
            logger.error(f"Error getting dashboard analytics: {str(e)}")
            raise

    def get_user_activity(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get user activity analytics."""
        try:
            return analytics_repository.get_user_activity(
                db,
                start_date=start_date,
                end_date=end_date,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            raise

    def get_content_analytics(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get content analytics."""
        try:
            return analytics_repository.get_content_analytics(
                db,
                start_date=start_date,
                end_date=end_date,
                content_type=content_type
            )
        except Exception as e:
            logger.error(f"Error getting content analytics: {str(e)}")
            raise

    def get_trends(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        metric: str
    ) -> Dict[str, Any]:
        """Get trend analysis for a specific metric."""
        try:
            return analytics_repository.get_trends(
                db,
                start_date=start_date,
                end_date=end_date,
                metric=metric
            )
        except Exception as e:
            logger.error(f"Error getting trends: {str(e)}")
            raise

    def get_analytics_summary(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get a summary of key analytics metrics."""
        try:
            return analytics_repository.get_analytics_summary(
                db,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            raise

# Create service instance
analytics_service = AnalyticsService() 