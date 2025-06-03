# Import all models here for Alembic to detect them
from sqlalchemy.orm import declarative_base
from app.models.user import User
from app.models.password import Password
from app.models.permission import Permission
from app.models.user_permission import UserPermission

# This is needed for Alembic to detect all models
__all__ = ["Base", "User", "Password", "Permission", "UserPermission"]

Base = declarative_base()

# Ensure tables are created in the correct order
def create_tables(engine):
    """Create all tables in the correct order."""
    # First create tables without foreign keys
    Base.metadata.create_all(bind=engine, tables=[
        User.__table__,
        Permission.__table__,
        Password.__table__
    ])
    
    # Then create tables with foreign keys
    Base.metadata.create_all(bind=engine, tables=[
        UserPermission.__table__
    ]) 