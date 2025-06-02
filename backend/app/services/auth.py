from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import verify_password, get_password_hash, create_access_token
from app.repositories.user import user_repository
from app.schemas.auth import UserCreate, UserLogin, Token
from app.models.user import User
from app.config.settings import get_settings
from app.core.exceptions import (
    DatabaseError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError
)

settings = get_settings()

class AuthService:
    def __init__(self):
        self.user_repository = user_repository

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def register(self, db: Session, user_in: UserCreate) -> dict:
        """Register a new user."""
        try:
            # Check if user exists
            if user_repository.get_by_email(db, email=user_in.email):
                raise UserAlreadyExistsError("Email already registered")
            
            # Hash password
            hashed_password = get_password_hash(user_in.password)
            
            # Create user
            user = user_repository.create(
                db=db,
                obj_in=user_in,
                hashed_password=hashed_password
            )
            
            return {
                "message": "Registration successful",
                "email": user.email
            }
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error during user registration: {str(e)}")

    def login(self, db: Session, user_in: UserLogin) -> Token:
        """Authenticate user and return token."""
        try:
            # Get user
            user = user_repository.get_by_email(db, email=user_in.email)
            if not user:
                raise InvalidCredentialsError()
            
            # Verify password
            if not verify_password(user_in.password, user.hashed_password):
                raise InvalidCredentialsError()
            
            # Check if user is active
            if not user.is_active:
                raise InactiveUserError()
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email},
                expires_delta=access_token_expires
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer"
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error during user login: {str(e)}")

# Create a singleton instance
auth_service = AuthService() 