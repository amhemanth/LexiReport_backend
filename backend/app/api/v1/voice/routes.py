from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
from app.models.core.user import User
from app.models.analytics import VoiceCommand  # Assuming model is here
from app.schemas.voice import (
    VoiceProfileCreate, VoiceProfileUpdate, VoiceProfileResponse,
    AudioCacheCreate, AudioCacheResponse, TextToSpeechRequest,
    TextToSpeechResponse, VoiceCommandCreate, VoiceCommandResponse
)
from app.services.voice import voice_service
from datetime import datetime
from .profile_routes import router as profile_router

router = APIRouter()

router.include_router(profile_router, prefix="", tags=["VoiceProfile"])

@router.post("/command", response_model=VoiceCommandResponse)
async def submit_voice_command(
    command_in: VoiceCommandCreate = Query(...),
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
    limit: int = Query(20, ge=1, le=100)
):
    """Get the user's voice command history."""
    commands = db.query(VoiceCommand).filter(VoiceCommand.user_id == current_user.id).order_by(VoiceCommand.created_at.desc()).limit(limit).all()
    return [VoiceCommandResponse.from_orm(cmd) for cmd in commands]

@router.get("/profiles", response_model=List[VoiceProfileResponse])
@require_permissions([Permission.READ_VOICE])
async def get_voice_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get voice profiles for the current user."""
    return voice_service.get_voice_profiles_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.get("/profiles/active", response_model=List[VoiceProfileResponse])
@require_permissions([Permission.READ_VOICE])
async def get_active_voice_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active voice profiles."""
    return voice_service.get_active_voice_profiles(
        db, skip=skip, limit=limit
    )

@router.get("/profiles/language/{language}", response_model=List[VoiceProfileResponse])
@require_permissions([Permission.READ_VOICE])
async def get_voice_profiles_by_language(
    language: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get voice profiles by language."""
    return voice_service.get_voice_profiles_by_language(
        db, language=language, skip=skip, limit=limit
    )

@router.post("/profiles", response_model=VoiceProfileResponse)
@require_permissions([Permission.WRITE_VOICE])
async def create_voice_profile(
    profile_in: VoiceProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new voice profile."""
    return voice_service.create_voice_profile(
        db, user_id=current_user.id, obj_in=profile_in
    )

@router.put("/profiles/{profile_id}", response_model=VoiceProfileResponse)
@require_permissions([Permission.WRITE_VOICE])
async def update_voice_profile(
    profile_id: str,
    profile_in: VoiceProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a voice profile."""
    return voice_service.update_voice_profile(
        db, profile_id=profile_id, obj_in=profile_in
    )

@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.WRITE_VOICE])
async def delete_voice_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a voice profile."""
    voice_service.delete_voice_profile(db, profile_id=profile_id)

@router.get("/cache/{profile_id}", response_model=List[AudioCacheResponse])
@require_permissions([Permission.READ_VOICE])
async def get_audio_cache(
    profile_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audio cache entries for a voice profile."""
    return voice_service.get_audio_cache_by_profile(
        db, profile_id=profile_id, skip=skip, limit=limit
    )

@router.post("/cache", response_model=AudioCacheResponse)
@require_permissions([Permission.WRITE_VOICE])
async def create_audio_cache(
    cache_in: AudioCacheCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new audio cache entry."""
    return voice_service.create_audio_cache(db, obj_in=cache_in)

@router.put("/cache/{cache_id}", response_model=AudioCacheResponse)
@require_permissions([Permission.WRITE_VOICE])
async def update_audio_cache(
    cache_id: str,
    cache_in: AudioCacheCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an audio cache entry."""
    return voice_service.update_audio_cache(
        db, cache_id=cache_id, obj_in=cache_in
    )

@router.delete("/cache/{cache_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.WRITE_VOICE])
async def delete_audio_cache(
    cache_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an audio cache entry."""
    voice_service.delete_audio_cache(db, cache_id=cache_id)

@router.post("/tts", response_model=TextToSpeechResponse)
@require_permissions([Permission.TEXT_TO_SPEECH])
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert text to speech using a voice profile."""
    return await voice_service.text_to_speech(
        db, profile_id=request.profile_id, text=request.text
    ) 