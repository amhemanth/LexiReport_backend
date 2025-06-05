from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.voice_profile import VoiceProfileCreate, VoiceProfileUpdate, VoiceProfileResponse
from app.services.voice import voice_service
import uuid

router = APIRouter()

@router.get("/profile", response_model=VoiceProfileResponse)
async def get_voice_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = voice_service.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")
    return VoiceProfileResponse.from_orm(profile)

@router.post("/profile", response_model=VoiceProfileResponse)
async def create_voice_profile(
    obj_in: VoiceProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = voice_service.create_profile(db, current_user.id, obj_in)
    return VoiceProfileResponse.from_orm(profile)

@router.put("/profile/{profile_id}", response_model=VoiceProfileResponse)
async def update_voice_profile(
    profile_id: int,
    obj_in: VoiceProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = voice_service.update_profile(db, profile_id, obj_in)
    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")
    return VoiceProfileResponse.from_orm(profile)

@router.delete("/profile/{profile_id}")
async def delete_voice_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    voice_service.delete_profile(db, profile_id)
    return {"status": "success"} 