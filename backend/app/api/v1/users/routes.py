from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.user import UserResponse, UserUpdate, UserList
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Update current user."""
    user = user_repository.update(
        db=db,
        db_obj=current_user,
        obj_in=user_in
    )
    return user

@router.put("/me/password")
def update_password(
    *,
    db: Session = Depends(get_db),
    password_in: PasswordUpdate,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Update current user's password."""
    try:
        # Verify current password
        if not verify_password(password_in.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Check if new password is same as current password
        if verify_password(password_in.new_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )
        
        # Hash new password
        hashed_password = get_password_hash(password_in.new_password)
        
        # Update password
        updated_user = user_repository.update(
            db=db,
            db_obj=current_user,
            obj_in=UserUpdate(),
            hashed_password=hashed_password
        )
        
        # Verify the update was successful
        if not updated_user or not verify_password(password_in.new_password, updated_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password. Please try again."
            )
        
        return {"message": "Password updated successfully"}
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating password"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/", response_model=UserList)
async def read_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of users."""
    skip = (page - 1) * size
    users = db.query(User).offset(skip).limit(size).all()
    total = db.query(User).count()
    pages = (total + size - 1) // size
    
    return UserList(
        items=users,
        total=total,
        page=page,
        size=size,
        pages=pages
    ) 