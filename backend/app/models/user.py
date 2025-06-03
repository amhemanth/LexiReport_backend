from sqlalchemy import Column, String, Boolean, DateTime, Enum, UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import uuid
from app.models.enums import UserRole
from app.models.permission import Permission as PermissionModel
from app.models.user_permission import UserPermission

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    passwords = relationship("Password", back_populates="user", cascade="all, delete-orphan")
    user_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if user has a specific permission.
        Admins automatically have all permissions.
        """
        # Admins have all permissions
        if self.role == UserRole.ADMIN:
            return True
            
        # Check specific permissions
        return any(
            up.permission.name == permission_name 
            for up in self.user_permissions
        )

    def get_permissions(self) -> list:
        """
        Get all permissions for the user.
        For admins, returns all available permissions.
        For regular users, returns only assigned permissions.
        """
        if self.role == UserRole.ADMIN:
            # Return all available permissions from the Permission enum
            from app.core.permissions import Permission
            return [p.value for p in Permission]
        else:
            # Return only assigned permissions
            return [up.permission.name for up in self.user_permissions]

    def add_permission(self, session, permission_name: str) -> bool:
        """
        Add a permission to the user.
        Returns True if permission was added, False if user already had it.
        """
        if self.has_permission(permission_name):
            return False

        # Validate permission name
        from app.core.permissions import Permission
        if permission_name not in [p.value for p in Permission]:
            raise ValueError(f"Permission {permission_name} does not exist")

        # Get the permission
        permission = session.query(PermissionModel).filter_by(name=permission_name).first()
        if not permission:
            raise ValueError(f"Permission {permission_name} does not exist")

        # Create user permission
        user_permission = UserPermission(
            id=uuid.uuid4(),
            user_id=self.id,
            permission_id=permission.id,
            created_at=datetime.now(timezone.utc)
        )
        session.add(user_permission)
        session.commit()
        return True

    def remove_permission(self, session, permission_name: str) -> bool:
        """
        Remove a permission from the user.
        Returns True if permission was removed, False if user didn't have it.
        """
        # Prevent removing critical permissions
        from app.core.permissions import Permission
        if permission_name == Permission.API_ACCESS.value:
            raise ValueError("Cannot remove api_access permission")

        if not self.has_permission(permission_name):
            return False

        # Find and remove the user permission
        for up in self.user_permissions:
            if up.permission.name == permission_name:
                session.delete(up)
                session.commit()
                return True
        return False 