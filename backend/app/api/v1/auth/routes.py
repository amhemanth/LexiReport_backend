from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, RegistrationResponse
from app.services.auth import AuthService
from app.repositories.user import UserRepository
from app.models.core.user import User

import uuid

router = APIRouter()

user_repository = UserRepository(User)
auth_service = AuthService(user_repository)

@router.post("/register", response_model=RegistrationResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    auth_service: AuthService = Depends(lambda: auth_service)
) -> dict:
    """Register a new user."""
    result = auth_service.register(db=db, user_in=user_in)
    user = auth_service.get_user_by_email(db, email=result["email"])
    return {
        "message": result["message"],
        "email": result["email"],
        "role": user.role,
        "permissions": user.get_permissions()
    }

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(lambda: auth_service)
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    # OAuth2 form uses 'username' field for email
    user_in = UserLogin(email=form_data.username, password=form_data.password)
    return auth_service.login(db=db, user_in=user_in) 