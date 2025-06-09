from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.core.security import verify_password, get_password_hash, create_access_token, ALGORITHM
from app.repositories.user import user_repository
from app.schemas.auth import UserCreate, UserLogin, Token, TokenData
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
    ValidationException
)
from app.core.permissions import Permission as PermissionEnum
from app.db.session import get_db
from app.schemas.user import UserUpdate, UserResponse

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

    def register(self, db: Session, user_in: UserCreate) -> dict:
        """Register a new user."""
        try:
            # Check if user exists
            if user_repository.get_by_email(db, email=user_in.email):
                raise UserAlreadyExistsError("Email already registered")
            
            # Hash password
            hashed_password = self.get_password_hash(user_in.password)
            
            # Create user with default role
            user = user_repository.create(
                db=db,
                obj_in=user_in,
                hashed_password=hashed_password,
                role=UserRole.USER,
                is_active=True
            )
            
            # Add default permissions
            default_permissions = [
                PermissionEnum.API_ACCESS.value,  # Basic API access
                PermissionEnum.READ_USERS.value,  # Can read own user data
                PermissionEnum.WRITE_USERS.value  # Can update own user data
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
            user = user_repository.get_by_email(db, email=user_in.email)
            if not user:
                raise InvalidCredentialsError()
            
            # Get current password
            current_password = user_repository.get_current_password(db, user.id)
            if not current_password:
                raise InvalidCredentialsError()
            
            # Verify password
            if not self.verify_password(user_in.password, current_password.hashed_password):
                raise InvalidCredentialsError()
            
            # Check if user is active
            if not user.is_active:
                raise InactiveUserError()
            
            # Create access token with role and permissions
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
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

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user."""
        user = self.user_repository.get_by_email(db, email=email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return UserResponse.from_orm(user)

    def get_current_user(self, db: Session, token: str) -> Optional[UserResponse]:
        """Get the current user from a JWT token."""
        payload = self.verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = self.get_user_by_id(db, user_id=uuid.UUID(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def get_current_active_user(self, db: Session, token: str) -> Optional[UserResponse]:
        """Get the current active user from a JWT token."""
        user = self.get_current_user(db, token=token)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user

    def get_current_active_superuser(self, db: Session, token: str) -> Optional[UserResponse]:
        """Get the current active superuser from a JWT token."""
        user = self.get_current_active_user(db, token=token)
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges"
            )
        return user

    def get_user_by_id(self, db: Session, *, user_id: uuid.UUID) -> Optional[UserResponse]:
        """Get a user by ID."""
        user = self.user_repository.get(db, id=user_id)
        if not user:
            raise NotFoundException("User not found")
        return UserResponse.from_orm(user)

    def get_user_by_email(self, db: Session, *, email: str) -> Optional[UserResponse]:
        """Get a user by email."""
        user = self.user_repository.get_by_email(db, email=email)
        if not user:
            raise NotFoundException("User not found")
        return UserResponse.from_orm(user)

    def get_users(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[UserResponse]:
        """Get a list of users."""
        users = self.user_repository.get_multi(db, skip=skip, limit=limit)
        return [UserResponse.from_orm(user) for user in users]

    def create_user(self, db: Session, *, obj_in: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if user with email already exists
        if self.user_repository.get_by_email(db, email=obj_in.email):
            raise ValidationException("Email already registered")
        
        # Create new user
        user = User(
            email=obj_in.email,
            hashed_password=self.get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            is_superuser=False
        )
        user = self.user_repository.create(db, obj_in=user)
        return UserResponse.from_orm(user)

    def update_user(
        self, db: Session, *, user_id: uuid.UUID, obj_in: UserUpdate
    ) -> UserResponse:
        """Update a user."""
        user = self.user_repository.get(db, id=user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Update user
        user = self.user_repository.update(db, db_obj=user, obj_in=obj_in)
        return UserResponse.from_orm(user)

    def delete_user(self, db: Session, *, user_id: uuid.UUID) -> None:
        """Delete a user."""
        user = self.user_repository.get(db, id=user_id)
        if not user:
            raise NotFoundException("User not found")
        self.user_repository.remove(db, id=user_id)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

# Create service instance
auth_service = AuthService(user_repository) 