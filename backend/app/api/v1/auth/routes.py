"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.services.auth import auth_service
from app.schemas.auth import TokenResponse, UserLogin
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=dict)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> dict:
    """Register a new user."""
    return auth_service.register(user_in)

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Login user and return tokens."""
    return auth_service.login(form_data.username, form_data.password)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Refresh access token."""
    return auth_service.refresh_token(refresh_token)

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: UserResponse = Depends(auth_service.get_current_user)
) -> UserResponse:
    """Get current user."""
    return current_user 