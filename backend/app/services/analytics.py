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

# Create service instance
analytics_service = AnalyticsService() 