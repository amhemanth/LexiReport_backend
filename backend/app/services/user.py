from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.exceptions import (
    DatabaseError,
    UserNotFoundError
)

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def get_user(self, db: Session, user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            user = self.user_repository.get(db, id=user_id)
            if not user:
                raise UserNotFoundError()
            return user
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving user: {str(e)}")

    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserResponse]:
        """Get list of users."""
        try:
            return self.user_repository.get_multi(db, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error retrieving users: {str(e)}")

    def update_user(
        self,
        db: Session,
        *,
        db_obj: UserResponse,
        obj_in: UserUpdate
    ) -> UserResponse:
        """Update user."""
        try:
            user = self.user_repository.update(db, db_obj=db_obj, obj_in=obj_in)
            if not user:
                raise UserNotFoundError()
            return user
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error updating user: {str(e)}")

    def delete_user(self, db: Session, *, user_id: int) -> None:
        """Delete user."""
        try:
            user = self.user_repository.get(db, id=user_id)
            if not user:
                raise UserNotFoundError()
            self.user_repository.remove(db, id=user_id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error deleting user: {str(e)}")

# Create a singleton instance
user_service = UserService() 