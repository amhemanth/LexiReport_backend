from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.schemas.file import FileUpload, FileResponse
from app.services.file import file_service
import uuid
import os
from app.config.settings import get_settings

router = APIRouter()
settings = get_settings()
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[FileResponse])
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [FileResponse.from_orm(f) for f in file_service.get_files(db, current_user.id)]

@router.post("/upload", response_model=FileResponse)
def upload_file(
    file: UploadFile = FastAPIFile(...),
    file_name: str = Body(...),
    file_type: str = Body(...),
    description: str = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Save file to disk
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    obj_in = FileUpload(file_name=file_name, file_type=file_type, description=description)
    return FileResponse.from_orm(file_service.upload_file(db, current_user.id, obj_in, file_location)) 