from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.user import UserResponse, UserUpdate, UserList

router = APIRouter()

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