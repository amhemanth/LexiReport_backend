from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.file import FileUpload, FileResponse
from app.services.file import file_service
import uuid

router = APIRouter()

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
    # Stub: Save file to disk/storage and get file_path
    file_path = f"/files/{file.filename}"
    obj_in = FileUpload(file_name=file_name, file_type=file_type, description=description)
    return FileResponse.from_orm(file_service.upload_file(db, current_user.id, obj_in, file_path)) 