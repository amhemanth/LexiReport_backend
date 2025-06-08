from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
from app.models.core.user import User
from app.schemas.voice import (
    VoiceProfileCreate, VoiceProfileUpdate, VoiceProfileResponse, VoiceProfileList,
    AudioCacheCreate, AudioCacheUpdate, AudioCacheResponse, AudioCacheList,
    TextToSpeechRequest, TextToSpeechResponse,
    VoiceCommandCreate, VoiceCommandUpdate, VoiceCommandResponse, VoiceCommandList
)
from app.services.voice import voice_service
from datetime import datetime
from .profile_routes import router as profile_router

router = APIRouter()

router.include_router(profile_router, prefix="", tags=["VoiceProfile"])

# Voice Command routes
@router.post("/commands", response_model=VoiceCommandResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.API_ACCESS])
async def create_voice_command(
    command: VoiceCommandCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new voice command."""
    return await voice_service.create_voice_command(db, user_id=current_user.id, obj_in=command)

@router.get("/commands", response_model=VoiceCommandList)
@require_permissions([Permission.API_ACCESS])
async def list_voice_commands(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    action_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List voice commands with optional filtering."""
    try:
        if status:
            commands = await voice_service.get_voice_commands_by_status(
                db, status=status, skip=skip, limit=limit
            )
        elif action_type:
            commands = await voice_service.get_voice_commands_by_action_type(
                db, action_type=action_type, skip=skip, limit=limit
            )
        else:
            commands = await voice_service.get_voice_commands_by_user(
                db, user_id=current_user.id, skip=skip, limit=limit
            )
        
        total = len(commands)  # TODO: Implement proper count
        return VoiceCommandList(
            items=commands,
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Voice Profile routes
@router.get("/profiles", response_model=VoiceProfileList)
@require_permissions([Permission.READ_VOICE])
async def list_voice_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    language: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List voice profiles with optional filtering."""
    try:
        if language:
            profiles = await voice_service.get_voice_profiles_by_language(
                db, language=language, skip=skip, limit=limit
            )
        else:
            profiles = await voice_service.get_voice_profiles_by_user(
                db, user_id=current_user.id, skip=skip, limit=limit
            )
        
        total = len(profiles)  # TODO: Implement proper count
        return VoiceProfileList(
            items=profiles,
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/profiles/active", response_model=VoiceProfileList)
@require_permissions([Permission.READ_VOICE])
async def list_active_voice_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List active voice profiles."""
    try:
        profiles = await voice_service.get_active_voice_profiles(
            db, skip=skip, limit=limit
        )
        total = len(profiles)  # TODO: Implement proper count
        return VoiceProfileList(
            items=profiles,
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/profiles", response_model=VoiceProfileResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_VOICE])
async def create_voice_profile(
    profile: VoiceProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new voice profile."""
    return await voice_service.create_voice_profile(
        db, user_id=current_user.id, obj_in=profile
    )

@router.put("/profiles/{profile_id}", response_model=VoiceProfileResponse)
@require_permissions([Permission.WRITE_VOICE])
async def update_voice_profile(
    profile_id: uuid.UUID,
    profile: VoiceProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a voice profile."""
    return await voice_service.update_voice_profile(
        db, profile_id=profile_id, obj_in=profile
    )

@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.WRITE_VOICE])
async def delete_voice_profile(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a voice profile."""
    await voice_service.delete_voice_profile(db, profile_id=profile_id)

# Audio Cache routes
@router.get("/cache", response_model=AudioCacheList)
@require_permissions([Permission.READ_VOICE])
async def list_audio_cache(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    voice_profile_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List audio cache entries with optional filtering."""
    try:
        if voice_profile_id:
            cache_entries = await voice_service.get_audio_cache_by_profile(
                db, voice_profile_id=voice_profile_id, skip=skip, limit=limit
            )
        else:
            # TODO: Implement get_all for audio cache
            cache_entries = []
        
        total = len(cache_entries)  # TODO: Implement proper count
        return AudioCacheList(
            items=cache_entries,
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/cache", response_model=AudioCacheResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_VOICE])
async def create_audio_cache(
    cache: AudioCacheCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new audio cache entry."""
    return await voice_service.create_audio_cache(db, obj_in=cache)

@router.put("/cache/{cache_id}", response_model=AudioCacheResponse)
@require_permissions([Permission.WRITE_VOICE])
async def update_audio_cache(
    cache_id: uuid.UUID,
    cache: AudioCacheUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an audio cache entry."""
    return await voice_service.update_audio_cache(
        db, cache_id=cache_id, obj_in=cache
    )

@router.delete("/cache/{cache_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.WRITE_VOICE])
async def delete_audio_cache(
    cache_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an audio cache entry."""
    await voice_service.delete_audio_cache(db, cache_id=cache_id)

# Text-to-Speech route
@router.post("/tts", response_model=TextToSpeechResponse)
@require_permissions([Permission.TEXT_TO_SPEECH])
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert text to speech using a voice profile."""
    return await voice_service.text_to_speech(db, request=request) 