from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, RegistrationResponse
from app.services.auth import auth_service

router = APIRouter()

@router.post("/register", response_model=RegistrationResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> dict:
    """Register a new user."""
    return auth_service.register(db=db, user_in=user_in)

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    user_in = UserLogin(email=form_data.username, password=form_data.password)
    return auth_service.login(db=db, user_in=user_in) 