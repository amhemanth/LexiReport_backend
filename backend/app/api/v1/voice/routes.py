from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.analytics import VoiceCommand  # Assuming model is here
from app.schemas.voice import VoiceCommandCreate, VoiceCommandResponse  # To be created if not present
from datetime import datetime

router = APIRouter()

@router.post("/command", response_model=VoiceCommandResponse)
async def submit_voice_command(
    command_in: VoiceCommandCreate = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a voice command (text or audio, intent classification stub)."""
    # For now, only support text commands
    command = VoiceCommand(
        user_id=current_user.id,
        command_text=command_in.command_text,
        action_type="stub_action",  # TODO: intent classification
        status="received",
        metadata={},
        created_at=datetime.utcnow()
    )
    db.add(command)
    db.commit()
    db.refresh(command)
    return VoiceCommandResponse.from_orm(command)

@router.get("/command-history", response_model=List[VoiceCommandResponse])
async def get_voice_command_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get the user's voice command history."""
    commands = db.query(VoiceCommand).filter(VoiceCommand.user_id == current_user.id).order_by(VoiceCommand.created_at.desc()).limit(limit).all()
    return [VoiceCommandResponse.from_orm(cmd) for cmd in commands] 