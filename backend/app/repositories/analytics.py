from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.analytics.voice_command import VoiceCommand
from app.schemas.analytics import (
    VoiceCommandCreate,
    VoiceCommandUpdate,
    VoiceCommandFilter,
    VoiceCommandResponse
)
from app.core.exceptions import NotFoundException
from app.repositories.base import BaseRepository
from datetime import datetime

class VoiceCommandRepository(BaseRepository[VoiceCommand, VoiceCommandCreate, VoiceCommandUpdate]):
    """Repository for voice command operations."""

    def get(self, db: Session, id: str) -> Optional[VoiceCommand]:
        """Get a voice command by ID."""
        return db.query(VoiceCommand).filter(VoiceCommand.id == id).first()

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by entity."""
        return db.query(VoiceCommand)\
            .filter(
                VoiceCommand.entity_type == entity_type,
                VoiceCommand.entity_id == entity_id
            )\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_action_type(
        self, db: Session, *, action_type: str,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by action type."""
        return self.get_multi_by_field(
            db, field="action_type", value=action_type, skip=skip, limit=limit
        )

    def get_by_status(
        self, db: Session, *, status: str,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Get voice commands by status."""
        return db.query(VoiceCommand)\
            .filter(VoiceCommand.status == status)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def create(self, db: Session, *, obj_in: VoiceCommandCreate) -> VoiceCommand:
        """Create a new voice command."""
        db_obj = VoiceCommand(
            user_id=obj_in.user_id,
            command_text=obj_in.command_text,
            action_type=obj_in.action_type,
            status=obj_in.status,
            entity_type=obj_in.entity_type,
            entity_id=obj_in.entity_id,
            meta_data=obj_in.meta_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: VoiceCommand, obj_in: VoiceCommandUpdate
    ) -> VoiceCommand:
        """Update a voice command."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: str) -> VoiceCommand:
        """Delete a voice command."""
        obj = db.query(VoiceCommand).get(id)
        if not obj:
            raise NotFoundException(f"Voice command with id {id} not found")
        db.delete(obj)
        db.commit()
        return obj

    def filter(
        self, db: Session, *, filter_obj: VoiceCommandFilter,
        skip: int = 0, limit: int = 100
    ) -> List[VoiceCommand]:
        """Filter voice commands based on criteria."""
        query = db.query(VoiceCommand)
        
        if filter_obj.user_id:
            query = query.filter(VoiceCommand.user_id == filter_obj.user_id)
        if filter_obj.action_type:
            query = query.filter(VoiceCommand.action_type == filter_obj.action_type)
        if filter_obj.status:
            query = query.filter(VoiceCommand.status == filter_obj.status)
        if filter_obj.entity_type:
            query = query.filter(VoiceCommand.entity_type == filter_obj.entity_type)
        if filter_obj.entity_id:
            query = query.filter(VoiceCommand.entity_id == filter_obj.entity_id)
        if filter_obj.start_date:
            query = query.filter(VoiceCommand.created_at >= filter_obj.start_date)
        if filter_obj.end_date:
            query = query.filter(VoiceCommand.created_at <= filter_obj.end_date)
            
        return query.offset(skip).limit(limit).all()

# Create repository instance
voice_command_repository = VoiceCommandRepository(VoiceCommand) 