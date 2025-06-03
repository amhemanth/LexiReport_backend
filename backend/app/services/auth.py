from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import verify_password, get_password_hash, create_access_token
from app.repositories.user import user_repository
from app.schemas.auth import UserCreate, UserLogin, Token
from app.models.user import User, UserRole
from app.models.permission import Permission as PermissionModel
from app.models.user_permission import UserPermission
from app.config.settings import get_settings
from app.core.exceptions import (
    DatabaseError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError
)
from app.core.permissions import Permission
import uuid

settings = get_settings()

class AuthService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    @staticmethod
    def get_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def _create_user_permission(self, db: Session, user_id: uuid.UUID, permission_name: str) -> None:
        """Create a user permission."""
        permission = db.query(PermissionModel).filter(PermissionModel.name == permission_name).first()
        if not permission:
            raise ValueError(f"Permission {permission_name} does not exist")

        user_permission = UserPermission(
            id=uuid.uuid4(),
            user_id=user_id,
            permission_id=permission.id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user_permission)

    def register(self, db: Session, user_in: UserCreate) -> dict:
        """Register a new user."""
        try:
            # Check if user exists
            if self.user_repository.get_by_email(db, email=user_in.email):
                raise UserAlreadyExistsError("Email already registered")
            
            # Hash password
            hashed_password = get_password_hash(user_in.password)
            
            # Create user with default role
            user = self.user_repository.create(
                db=db,
                obj_in=user_in,
                hashed_password=hashed_password,
                role=UserRole.USER,
                is_active=True
            )
            
            # Add default permissions
            default_permissions = [
                Permission.API_ACCESS.value,  # Basic API access
                Permission.READ_USERS.value,  # Can read own user data
                Permission.WRITE_USERS.value  # Can update own user data
            ]
            
            for permission in default_permissions:
                self._create_user_permission(db, user.id, permission)
            
            db.commit()
            
            return {
                "message": "Registration successful",
                "email": user.email
            }
        except SQLAlchemyError as e:
            db.rollback()
            raise DatabaseError(f"Error during user registration: {str(e)}")

    def login(self, db: Session, user_in: UserLogin) -> Token:
        """Authenticate user and return token."""
        try:
            # Get user
            user = self.user_repository.get_by_email(db, email=user_in.email)
            if not user:
                raise InvalidCredentialsError()
            
            # Get current password
            current_password = self.user_repository.get_current_password(db, user.id)
            if not current_password:
                raise InvalidCredentialsError()
            
            # Verify password
            if not verify_password(user_in.password, current_password.hashed_password):
                raise InvalidCredentialsError()
            
            # Check if user is active
            if not user.is_active:
                raise InactiveUserError()
            
            # Create access token with role and permissions
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user.email,
                    "role": user.role.value,
                    "permissions": user.get_permissions()
                },
                expires_delta=access_token_expires
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                role=user.role,
                permissions=user.get_permissions()
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error during user login: {str(e)}") 