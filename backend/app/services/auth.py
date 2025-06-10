"""Authentication service."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid
import time
from redis import Redis
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    verify_token, validate_password_strength, generate_password_reset_token,
    verify_password_reset_token, generate_email_verification_token
)
from app.repositories.user import user_repository
from app.schemas.auth import (
    TokenResponse, TokenData, PasswordResetRequest, PasswordResetConfirm,
    LoginAttempt, LoginResponse, RegisterRequest, EmailVerificationRequest
)
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.core.user import User
from app.models.core.user_permission import UserPermission
from app.models.core.permission import Permission
from app.models.core.password import Password
from app.models.core.login_attempt import LoginAttempt
from app.config.settings import get_settings
from app.core.exceptions import (
    DatabaseError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError,
    NotFoundException,
    PermissionException,
    ValidationException,
    AuthenticationError,
    SecurityException,
    RateLimitExceededError
)
from app.core.permissions import Permission as PermissionEnum
from app.db.session import get_db
from app.core.logger import logger
from app.core.email import send_verification_email
from app.services.email import email_service
from app.models.core.enums import UserRole

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Running without Redis.")
            self.redis_client = None

        self.max_login_attempts = 5
        self.lockout_duration = 300  # 5 minutes in seconds
        self.max_sessions = 5  # Maximum number of concurrent sessions per user
        self.login_attempts = {}  # Store login attempts
        self.user_sessions = {}  # Store user sessions

    def _get_login_attempts_key(self, email: str) -> str:
        """Get Redis key for login attempts."""
        return f"login_attempts:{email}"

    def _get_lockout_key(self, email: str) -> str:
        """Get Redis key for account lockout."""
        return f"account_lockout:{email}"

    def _get_user_sessions_key(self, user_id: str) -> str:
        """Get Redis key for user sessions."""
        return f"user_sessions:{user_id}"

    def _check_rate_limit(self, email: str) -> None:
        """Check if user has exceeded login attempts."""
        if not self.redis_client:
            return

        try:
            lockout_key = self._get_lockout_key(email)
            if self.redis_client.exists(lockout_key):
                remaining_time = self.redis_client.ttl(lockout_key)
                raise RateLimitExceededError(
                    f"Account temporarily locked. Please try again in {remaining_time} seconds."
                )
        except Exception as e:
            logger.warning(f"Rate limit check failed: {str(e)}")

    def _increment_login_attempts(self, email: str) -> None:
        """Increment failed login attempts."""
        if not self.redis_client:
            return

        try:
            attempts_key = self._get_login_attempts_key(email)
            attempts = self.redis_client.incr(attempts_key)
            
            # Set expiry on first attempt
            if attempts == 1:
                self.redis_client.expire(attempts_key, 3600)  # 1 hour
            
            # Lock account if max attempts reached
            if attempts >= self.max_login_attempts:
                lockout_key = self._get_lockout_key(email)
                self.redis_client.setex(lockout_key, self.lockout_duration, "1")
                raise RateLimitExceededError(
                    f"Too many failed attempts. Account locked for {self.lockout_duration} seconds."
                )
        except Exception as e:
            logger.warning(f"Login attempts increment failed: {str(e)}")

    def _reset_login_attempts(self, email: str) -> None:
        """Reset failed login attempts."""
        if not self.redis_client:
            return

        try:
            attempts_key = self._get_login_attempts_key(email)
            lockout_key = self._get_lockout_key(email)
            self.redis_client.delete(attempts_key, lockout_key)
        except Exception as e:
            logger.warning(f"Login attempts reset failed: {str(e)}")

    def _manage_user_sessions(self, user_id: str, session_id: str) -> None:
        """Manage user sessions to prevent too many concurrent logins."""
        if not self.redis_client:
            return

        try:
            sessions_key = self._get_user_sessions_key(user_id)
            
            # Get current sessions
            current_sessions = self.redis_client.smembers(sessions_key)
            
            # If max sessions reached, remove oldest session
            if len(current_sessions) >= self.max_sessions:
                oldest_session = current_sessions.pop()
                self.redis_client.srem(sessions_key, oldest_session)
            
            # Add new session
            self.redis_client.sadd(sessions_key, session_id)
            self.redis_client.expire(sessions_key, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        except Exception as e:
            logger.warning(f"Session management failed: {str(e)}")

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
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def _ensure_permission_exists(self, db: Session, permission_name: str) -> Permission:
        """Ensure a permission exists in the database."""
        permission = db.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            # Create the permission if it doesn't exist
            permission = Permission(
                id=uuid.uuid4(),
                name=permission_name,
                description=f"Permission for {permission_name}",
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
                is_active=True
            )
            db.add(user_permission)

    async def register(self, db: Session, user_data: RegisterRequest) -> User:
        """Register a new user."""
        try:
            # Check if email already exists
            existing_user = user_repository.get_by_email(db, email=user_data.email)
            if existing_user:
                raise ValidationException(
                    f"An account with email {user_data.email} already exists. "
                    "Please use a different email address or try logging in."
                )
            
            # Check if username already exists (if provided)
            if user_data.username:
                existing_username = user_repository.get_by_username(db, username=user_data.username)
                if existing_username:
                    raise ValidationException(
                        f"Username '{user_data.username}' is already taken. "
                        "Please choose a different username."
                    )
            
            # Validate password strength
            is_valid, error_message = validate_password_strength(user_data.password)
            if not is_valid:
                raise ValidationException(error_message)
            
            # Generate username from email if not provided
            username = user_data.username or user_data.email.split('@')[0]
            # Ensure username is unique by appending a number if needed
            base_username = username
            counter = 1
            while user_repository.get_by_username(db, username=username):
                username = f"{base_username}{counter}"
                counter += 1
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            user = user_repository.create(
                db,
                obj_in=UserCreate(
                    email=user_data.email,
                    username=username,
                    password=hashed_password,
                    full_name=user_data.full_name or user_data.email.split('@')[0],
                    is_superuser=False,
                    role=UserRole.USER,
                    is_active=True,
                    email_verified=True  # Disable email verification
                ),
                hashed_password=hashed_password,
                role=UserRole.USER,
                is_active=True
            )
            
            # Assign default permissions
            self._assign_default_permissions(db, user.id)
            
            return user
                
        except ValidationException as e:
            # No need to rollback here as no database changes were made
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error during registration: {str(e)}")
            raise DatabaseError("An unexpected error occurred. Please try again.")

    async def verify_email(self, db: Session, token: str) -> Dict[str, Any]:
        """Verify user email."""
        try:
            # Verify token
            email = verify_token(token, token_type="email_verification")
            if not email:
                raise ValidationException("Invalid or expired verification token")
            
            # Get user
            user = user_repository.get_by_email(db, email=email)
            if not user:
                raise ValidationException("User not found")
            
            # Update user
            user_repository.update(
                db,
                db_obj=user,
                obj_in={"email_verified": True}
            )
            
            return {
                "message": "Email verified successfully",
                "verified": True
            }
            
        except ValidationException as e:
            logger.error(f"Validation error during email verification: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during email verification: {str(e)}")
            raise DatabaseError("Failed to verify email")

    async def login(self, db: Session, username_or_email: str, password: str, request: Request) -> LoginResponse:
        """Authenticate user and return tokens with enhanced security."""
        try:
            # Check rate limiting
            self._check_rate_limit(username_or_email)
            
            # Get user by email or username
            user = user_repository.get_by_email(db, email=username_or_email)
            if not user:
                # Try username if email not found
                user = user_repository.get_by_username(db, username=username_or_email)
                if not user:
                    self._increment_login_attempts(username_or_email)
                    logger.error(f"Login attempt failed: User not found for {username_or_email}")
                    raise AuthenticationError("Invalid credentials")
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {username_or_email}")
                raise InactiveUserError("User account is inactive")

            # Check if email is verified (if the field exists)
            if not getattr(user, 'email_verified', True):
                logger.warning(f"Login attempt for unverified email: {username_or_email}")
                raise ValidationException("Email not verified")
            
            # Get current password
            password_record = db.query(Password).filter(
                Password.user_id == user.id,
                Password.is_current == True
            ).first()
            if not password_record:
                logger.error(f"Login attempt failed: No password found for user {user.id}")
                raise AuthenticationError("Invalid credentials")
            
            # Verify password
            if not verify_password(password, password_record.hashed_password):
                self._increment_login_attempts(username_or_email)
                logger.error(f"Login attempt failed: Invalid password for user {user.id}")
                raise AuthenticationError("Invalid credentials")
            
            # Reset login attempts on successful login
            self._reset_login_attempts(username_or_email)
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Manage user sessions
            self._manage_user_sessions(str(user.id), session_id)
            
            # Generate tokens
            access_token = create_access_token(
                subject=str(user.id),
                session_id=session_id
            )
            refresh_token = create_refresh_token(
                subject=str(user.id),
                session_id=session_id
            )
            
            # Log successful login
            logger.info(f"User {user.id} logged in successfully")
            
            # Record login attempt
            login_attempt = LoginAttempt(
                user_id=user.id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                success=True
            )
            db.add(login_attempt)
            db.commit()
            
            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=UserResponse.from_orm(user),
                session_id=session_id
            )
            
        except AuthenticationError as e:
            logger.error(f"Authentication error during login: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise DatabaseError("Failed to login")

    async def logout(self, db: Session, user_id: str, session_id: str) -> Dict[str, str]:
        """Logout user and invalidate session."""
        try:
            # Remove session from Redis
            sessions_key = self._get_user_sessions_key(user_id)
            self.redis_client.srem(sessions_key, session_id)
            
            return {"message": "Logged out successfully"}
            
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            raise DatabaseError("Failed to logout")

    async def refresh_token(self, db: Session, refresh_token: str) -> TokenResponse:
        """Refresh access token with enhanced security."""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, token_type="refresh")
            if not payload:
                raise AuthenticationError("Invalid refresh token")
            
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid refresh token payload")
            
            # Get user
            user = user_repository.get(db, id=user_id)
            if not user:
                raise AuthenticationError("User not found")
            
            if not user.is_active:
                raise AuthenticationError("User account is inactive")
            
            # Generate new tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            new_refresh_token = create_refresh_token(
                data={"sub": str(user.id)}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
            
        except AuthenticationError as e:
            logger.error(f"Authentication error during token refresh: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            raise DatabaseError("Failed to refresh token")

    async def request_password_reset(self, db: Session, email: str) -> Dict[str, str]:
        """Request password reset."""
        try:
            user = user_repository.get_by_email(db, email=email)
            if not user:
                # Don't reveal if email exists
                return {"message": "If the email exists, a password reset link has been sent"}
            
            # Generate reset token
            reset_token = generate_password_reset_token(email)
            
            # TODO: Send email with reset token
            # For now, just return the token
            return {
                "message": "Password reset link has been sent",
                "reset_token": reset_token  # Remove this in production
            }
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            raise DatabaseError("Failed to request password reset")

    async def reset_password(
        self,
        db: Session,
        reset_data: PasswordResetConfirm
    ) -> Dict[str, str]:
        """Reset password using reset token."""
        try:
            # Verify reset token
            email = verify_password_reset_token(reset_data.reset_token)
            if not email:
                raise ValidationException("Invalid or expired reset token")
            
            # Get user
            user = user_repository.get_by_email(db, email=email)
            if not user:
                raise ValidationException("User not found")
            
            # Validate new password
            is_valid, error_message = validate_password_strength(reset_data.new_password)
            if not is_valid:
                raise ValidationException(error_message)
            
            # Update password
            hashed_password = get_password_hash(reset_data.new_password)
            user_repository.update(
                db,
                db_obj=user,
                obj_in={"hashed_password": hashed_password}
            )
            
            return {"message": "Password has been reset successfully"}
            
        except ValidationException as e:
            logger.error(f"Validation error during password reset: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during password reset: {str(e)}")
            raise DatabaseError("Failed to reset password")

    def _assign_default_permissions(self, db: Session, user_id: uuid.UUID) -> None:
        """Assign default permissions to a new user."""
        from app.core.permissions import Permission
        
        default_permissions = [
            Permission.API_ACCESS,
            Permission.READ_COMMENTS,
            Permission.WRITE_COMMENTS
        ]
        
        for permission in default_permissions:
            self._create_user_permission(db, user_id, permission.value)

    def _check_login_attempts(self, email: str) -> None:
        """
        Check if user has exceeded login attempts.
        
        Args:
            email: User's email address
            
        Raises:
            AuthenticationError: If user has exceeded login attempts
        """
        if email in self.login_attempts:
            attempts, last_attempt = self.login_attempts[email]
            if attempts >= settings.MAX_LOGIN_ATTEMPTS:
                time_diff = datetime.utcnow() - last_attempt
                if time_diff < timedelta(minutes=settings.LOGIN_ATTEMPT_WINDOW_MINUTES):
                    raise AuthenticationError(
                        f"Too many login attempts. Please try again in "
                        f"{settings.LOGIN_ATTEMPT_WINDOW_MINUTES - time_diff.seconds // 60} minutes."
                    )
                else:
                    # Reset attempts if window has passed
                    self.login_attempts[email] = (0, datetime.utcnow())
    
    def _record_login_attempt(self, email: str, success: bool) -> None:
        """
        Record a login attempt.
        
        Args:
            email: User's email address
            success: Whether the login attempt was successful
        """
        if success:
            if email in self.login_attempts:
                del self.login_attempts[email]
        else:
            if email in self.login_attempts:
                attempts, _ = self.login_attempts[email]
                self.login_attempts[email] = (attempts + 1, datetime.utcnow())
            else:
                self.login_attempts[email] = (1, datetime.utcnow())

# Create a singleton instance
auth_service = AuthService() 