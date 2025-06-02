# Import all models here for Alembic to detect them
from app.db.base_class import Base
from app.models.user import User  # noqa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() 