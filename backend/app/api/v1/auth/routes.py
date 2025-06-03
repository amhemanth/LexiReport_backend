from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, RegistrationResponse
from app.services.auth import auth_service
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=RegistrationResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
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
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    user_in = UserLogin(email=form_data.username, password=form_data.password)
    token = auth_service.login(db=db, user_in=user_in)
    user = auth_service.get_user_by_email(db, email=user_in.email)
    return Token(
        access_token=token.access_token,
        token_type=token.token_type,
        role=user.role,
        permissions=user.get_permissions()
    ) 