# Import all models here for Alembic to detect them
from app.db.base_class import Base
from app.models.user import User
from app.models.password import Password
from app.models.permission import Permission
from app.models.user_permission import UserPermission

# This is needed for Alembic to detect all models
__all__ = ["Base", "User", "Password", "Permission", "UserPermission"] 