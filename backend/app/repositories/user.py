from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.core.user import User, UserRole as UserRoleEnum
from app.models.core.permission import Role
from app.models.core.user_role import UserRole
from app.models.core.password import Password
from app.schemas.user import UserCreate, UserUpdate
from datetime import datetime, timezone
import uuid

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with user-specific operations."""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    def create(
        self,
        db: Session,
        *,
        obj_in: UserCreate,
        hashed_password: str,
        role: UserRoleEnum = UserRoleEnum.USER,
        is_active: bool = True
    ) -> User:
        """Create a new user."""
        # Create user
        db_obj = User(
            id=uuid.uuid4(),
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            is_active=is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(db_obj)
        db.flush()  # Flush to get the user ID

        # Create password record
        password = Password(
            id=uuid.uuid4(),
            user_id=db_obj.id,
            hashed_password=hashed_password,
            password_updated_at=datetime.now(timezone.utc),
            is_current=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(password)

        # Get role from database
        role_obj = db.query(Role).filter(Role.name == role.value).first()
        if not role_obj:
            raise ValueError(f"Role {role.value} not found in database")

        # Create user role
        user_role = UserRole(
            id=uuid.uuid4(),
            user_id=db_obj.id,
            role_id=role_obj.id,  # Use the role ID from the database
            is_primary=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(user_role)

        db.commit()  # Commit the transaction
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: UserUpdate,
        hashed_password: Optional[str] = None,
        password_updated_at: Optional[datetime] = None
    ) -> User:
        """Update a user.
        
        This method updates the user's data. If hashed_password is provided, it creates a new password record
        and marks the old one as not current.
        """
        update_data = obj_in.dict(exclude_unset=True)
        
        # Update user data
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db_obj.updated_at = datetime.now(timezone.utc)
        
        # Handle password update if provided
        if hashed_password:
            # Mark current password as not current
            current_password = db.query(Password).filter(
                Password.user_id == db_obj.id,
                Password.is_current == True
            ).first()
            if current_password:
                current_password.is_current = False
                db.add(current_password)
            
            # Create new password record
            new_password = Password(
                id=uuid.uuid4(),
                user_id=db_obj.id,
                hashed_password=hashed_password,
                password_updated_at=password_updated_at or datetime.now(timezone.utc),
                is_current=True,
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_password)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        return db.query(self.model)\
            .filter(self.model.is_active == True)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def count_users(self, db: Session) -> int:
        """Count total users."""
        return db.query(self.model).count()

    def get_current_password(self, db: Session, user_id: uuid.UUID) -> Optional[Password]:
        """Get user's current password."""
        return db.query(Password).filter(
            Password.user_id == user_id,
            Password.is_current == True
        ).first()

    def update_user(self, db: Session, user_id: uuid.UUID, user_data: dict) -> Optional[User]:
        """Update user data."""
        user = self.get(db, user_id)
        if user:
            return self.update(db, db_obj=user, obj_in=UserUpdate(**user_data))
        return None

    def delete_user(self, db: Session, user_id: uuid.UUID) -> bool:
        """Delete user."""
        user = self.get(db, user_id)
        if user:
            self.remove(db, id=user_id)
            return True
        return False

# Singleton instance for use in services
user_repository = UserRepository(User) 