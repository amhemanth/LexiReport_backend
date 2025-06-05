# Import base class and all models for Alembic to detect them
from app.models import *  # noqa

# Export all models for Alembic
from app.models import __all__  # noqa

# Optionally, you can define a create_tables function if you need to create tables manually
# def create_tables(engine):
#     Base.metadata.create_all(bind=engine) 