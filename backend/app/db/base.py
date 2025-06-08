"""Base class for database models."""
from app.db.base_class import Base
from app.models.core import *
from app.models.reports import *
from app.models.analytics import *
from app.models.notifications import *
from app.models.audit import *
from app.models.files import *
from app.models.comments import *
from app.models.tags import *
from app.models.processing import *
from app.models.integration import *
from app.models.media import *

# No need to define __all__ here since we're importing everything from models/__init__.py