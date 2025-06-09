import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent))

from alembic.config import Config
from alembic import command
from app.config.settings import get_settings
from app.db.base import Base

settings = get_settings()

def run_migrations():
    """Run database migrations."""
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Set the database URL
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))
    
    # Run the migration
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully.")

if __name__ == "__main__":
    run_migrations() 