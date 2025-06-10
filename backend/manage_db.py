"""Database management script."""
import argparse
import logging
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy_utils import database_exists, create_database, drop_database
from app.config.settings import get_settings
from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.db.scripts.seed_db import seed_database, SeedingError
from alembic.config import Config
from alembic import command
from contextlib import contextmanager
import time
from typing import Optional, List, Dict, Any
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@contextmanager
def handle_database_errors():
    """Context manager for handling database errors."""
    try:
        yield
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}", exc_info=True)
        raise

def load_seed_config(config_path: Optional[str] = None) -> Optional[Dict]:
    """Load seed configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Optional[Dict]: Configuration dictionary if file exists, None otherwise
    """
    if not config_path:
        return None
        
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading seed configuration: {str(e)}")
        return None

def run_migrations(version: Optional[str] = None):
    """Run database migrations."""
    with handle_database_errors():
        alembic_cfg = Config("alembic.ini")
        if version:
            command.upgrade(alembic_cfg, version)
        else:
            command.upgrade(alembic_cfg, "head")

def init_database(force: bool = False):
    """Initialize the database.
    
    Args:
        force: If True, will recreate the database even if it exists.
    """
    settings = get_settings()
    
    with handle_database_errors():
        # Create database if it doesn't exist
        db_url = str(settings.SQLALCHEMY_DATABASE_URI)
        if not database_exists(db_url):
            create_database(db_url)
            logger.info("Database created successfully.")
        elif force:
            logger.info("Force flag set, recreating database...")
            drop_database(db_url)
            create_database(db_url)
            logger.info("Database recreated successfully.")
        else:
            logger.info("Database already exists.")
        
        # Run migrations
        run_migrations()
        logger.info("Database initialization completed successfully.")

def reset_database_safe(confirm: bool = False):
    """Safely reset the database with proper error handling.
    
    Args:
        confirm: If True, skips confirmation prompt.
    """
    if not confirm:
        response = input("Are you sure you want to reset the database? This will delete all data. (y/N): ")
        if response.lower() != 'y':
            logger.info("Database reset cancelled.")
            return

    settings = get_settings()
    db_url = str(settings.SQLALCHEMY_DATABASE_URI)
    
    with handle_database_errors():
        # Drop all tables first
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully.")
        
        if database_exists(db_url):
            drop_database(db_url)
            logger.info("Database dropped successfully.")
        else:
            logger.info("Database does not exist, skipping drop.")
        
        create_database(db_url)
        logger.info("Database recreated successfully.")
        
        # Run migrations
        run_migrations()
        logger.info("Database reset completed successfully.")

def seed_database_safe(force: bool = False, config_path: Optional[str] = None):
    """Safely seed the database with proper error handling.
    
    Args:
        force: If True, will reseed even if data exists
        config_path: Optional path to seed configuration file
    """
    with handle_database_errors():
        # Load seed configuration if provided
        config = load_seed_config(config_path)
        
        # Check if data already exists
        if not force:
            with SessionLocal() as db:
                from app.models.core import User
                user_count = db.query(User).count()
                if user_count > 0:
                    logger.warning("Database already contains data. Use --force to reseed.")
                    return

        # Ensure schema is up-to-date before seeding
        run_migrations()
        
        # Create a new session for seeding
        with SessionLocal() as db:
            try:
                seed_database(db, force=force)
                logger.info("Database seeding completed successfully.")
            except Exception as e:
                db.rollback()
                logger.error(f"Error seeding database: {str(e)}")
                raise

def get_database_info() -> Dict[str, Any]:
    """Get database information."""
    with handle_database_errors():
        inspector = inspect(engine)
        return {
            "tables": inspector.get_table_names(),
            "views": inspector.get_view_names(),
            "schemas": inspector.get_schema_names()
        }

def check_database_health() -> bool:
    """Check database health."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def backup_database():
    """Create database backup."""
    settings = get_settings()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{settings.POSTGRES_DB}_{timestamp}.sql"
    
    with handle_database_errors():
        # Create backup directory if it doesn't exist
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Create backup using pg_dump
        backup_path = backup_dir / backup_file
        os.system(f'pg_dump -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -p {settings.POSTGRES_PORT} {settings.POSTGRES_DB} > {backup_path}')
        logger.info(f"Database backup created at {backup_path}")

def main():
    parser = argparse.ArgumentParser(description='Database management commands')
    parser.add_argument('command', choices=['init', 'reset', 'seed', 'reset-and-seed', 'migrate', 'info', 'health', 'backup'],
                      help='Command to run: init (create DB and tables), reset (drop and recreate DB), seed (populate with initial data), reset-and-seed (both), migrate (run migrations), info (show DB info), health (check DB health), or backup (create DB backup)')
    parser.add_argument('--force', action='store_true', help='Force operation even if data exists')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompts')
    parser.add_argument('--version', help='Specific migration version to use')
    parser.add_argument('--config', help='Path to seed configuration file')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            logger.info("Initializing database...")
            init_database(force=args.force)
        elif args.command == 'reset':
            logger.info("Resetting database...")
            reset_database_safe(confirm=args.confirm)
        elif args.command == 'seed':
            logger.info("Seeding database...")
            seed_database_safe(force=args.force, config_path=args.config)
        elif args.command == 'reset-and-seed':
            logger.info("Starting reset-and-seed process...")
            reset_database_safe(confirm=args.confirm)
            seed_database_safe(force=args.force, config_path=args.config)
            logger.info("Reset and seed process completed successfully")
        elif args.command == 'migrate':
            logger.info("Running migrations...")
            run_migrations(version=args.version)
        elif args.command == 'info':
            info = get_database_info()
            logger.info("Database Information:")
            for key, value in info.items():
                logger.info(f"{key}: {value}")
        elif args.command == 'health':
            is_healthy = check_database_health()
            if is_healthy:
                logger.info("Database is healthy")
            else:
                logger.error("Database health check failed")
                sys.exit(1)
        elif args.command == 'backup':
            logger.info("Creating database backup...")
            backup_database()
            
        logger.info(f"Command '{args.command}' completed successfully.")
        
    except Exception as e:
        logger.error(f"Error executing command '{args.command}': {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 