"""Authentication service."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.repositories.user import user_repository
from app.schemas.auth import TokenResponse, TokenData
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.core.user import User, UserRole
from app.models.core.user_permission import UserPermission
from app.models.core.permission import Permission
from app.config.settings import get_settings
from app.core.exceptions import (
    DatabaseError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError,
    NotFoundException,
    PermissionException,
    ValidationException,
    AuthenticationError
)
from app.core.permissions import Permission as PermissionEnum
from app.db.session import get_db
from app.core.logger import logger

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_repository):
        """Initialize the auth service with dependencies."""
        self.user_repository = user_repository
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a new access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    @staticmethod
    def get_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def _ensure_permission_exists(self, db: Session, permission_name: str) -> Permission:
        """Ensure a permission exists in the database."""
        permission = db.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            # Create the permission if it doesn't exist
            permission = Permission(
                id=uuid.uuid4(),
                name=permission_name,
                description=f"Permission for {permission_name}",
                module="core",
                action=permission_name,
                is_active=True
            )
            db.add(permission)
            db.flush()
        return permission

    def _create_user_permission(self, db: Session, user_id: uuid.UUID, permission_name: str) -> None:
        """Create a user permission."""
        permission = self._ensure_permission_exists(db, permission_name)
        
        # Check if user already has this permission
        existing = db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission.id
        ).first()
        
        if not existing:
            user_permission = UserPermission(
                id=uuid.uuid4(),
                user_id=user_id,
                permission_id=permission.id,
                granted_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(user_permission)

    def register(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user."""
        try:
            # Check if user already exists
            if self.user_repository.get_by_email(self.user_repository.db, email=user_data.email):
                raise ValidationException("Email already registered")
            
            # Hash password
            hashed_password = self.get_password_hash(user_data.password)
            
            # Create user
            user = self.user_repository.create(
                self.user_repository.db,
                obj_in=UserCreate(
                    **user_data.dict(exclude={'password'}),
                    hashed_password=hashed_password,
                    is_active=True
                )
            )
            
            # Assign default permissions
            self._assign_default_permissions(user.id)
            
            return {
                "message": "User registered successfully",
                "user_id": str(user.id)
            }
            
        except ValidationException as e:
            logger.error(f"Validation error during registration: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            raise DatabaseError("Failed to register user")

    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])

    def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return tokens."""
        try:
            # Get user
            user = self.user_repository.get_by_email(self.user_repository.db, email=email)
            if not user:
                raise AuthenticationError("Invalid credentials")
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                raise AuthenticationError("Invalid credentials")
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("User account is inactive")
            
            # Generate tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            refresh_token = create_refresh_token(
                data={"sub": str(user.id)}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
            
        except AuthenticationError as e:
            logger.error(f"Authentication error during login: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise DatabaseError("Failed to authenticate user")

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token)
            if not payload:
                raise AuthenticationError("Invalid refresh token")
            
            # Get user
            user = self.user_repository.get(self.user_repository.db, id=payload.get("sub"))
            if not user:
                raise AuthenticationError("User not found")
            
            # Generate new access token
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
            
        except AuthenticationError as e:
            logger.error(f"Authentication error during token refresh: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            raise DatabaseError("Failed to refresh token")

    def get_current_user(self, token: str) -> User:
        """Get current user from token."""
        try:
            # Verify token
            payload = verify_token(token)
            if not payload:
                raise AuthenticationError("Invalid token")
            
            # Get user
            user = self.user_repository.get(self.user_repository.db, id=payload.get("sub"))
            if not user:
                raise AuthenticationError("User not found")
            
            return user
            
        except AuthenticationError as e:
            logger.error(f"Authentication error getting current user: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            raise DatabaseError("Failed to get current user")

    def _assign_default_permissions(self, user_id: str) -> None:
        """Assign default permissions to user."""
        try:
            # Get default role
            default_role = self.user_repository.db.query(UserRole).filter(
                UserRole.name == "user"
            ).first()
            
            if default_role:
                # Create user role
                user_role = UserRole(
                    user_id=user_id,
                    role_id=default_role.id,
                    is_primary=True
                )
                self.user_repository.db.add(user_role)
                
                # Get role permissions
                role_permissions = self.user_repository.db.query(Permission).join(
                    UserPermission
                ).filter(
                    UserPermission.role_id == default_role.id
                ).all()
                
                # Assign permissions to user
                for permission in role_permissions:
                    user_permission = UserPermission(
                        user_id=user_id,
                        permission_id=permission.id
                    )
                    self.user_repository.db.add(user_permission)
                
                self.user_repository.db.commit()
                
        except Exception as e:
            self.user_repository.db.rollback()
            logger.error(f"Error assigning default permissions: {str(e)}")
            raise DatabaseError("Failed to assign default permissions")

# Create service instance
auth_service = AuthService(user_repository) 