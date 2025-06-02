from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with user-specific operations."""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate, hashed_password: str) -> User:
        """Create a new user."""
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: UserUpdate,
        hashed_password: Optional[str] = None
    ) -> User:
        """Update a user."""
        update_data = obj_in.dict(exclude_unset=True)
        if hashed_password:
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

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

    async def update_user(self, db: Session, user_id: int, user_data: dict) -> Optional[User]:
        """Update user data."""
        user = await self.get(db, user_id)
        if user:
            return await self.update(db, user, user_data)
        return None

    async def delete_user(self, db: Session, user_id: int) -> bool:
        """Delete user."""
        user = await self.get(db, user_id)
        if user:
            await self.delete(db, user_id)
            return True
        return False

# Create a singleton instance
user_repository = UserRepository(User) 