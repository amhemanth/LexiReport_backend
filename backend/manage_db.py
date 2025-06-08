"""Database management script."""
import argparse
import logging
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
from app.config.settings import get_settings
from app.db.base_class import Base
from app.db.session import engine
from app.db.scripts.reset_db import reset_database
from app.db.scripts.seed_db import seed
from alembic.config import Config
from alembic import command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations."""
    try:
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully.")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise

def init_database():
    """Initialize the database."""
    settings = get_settings()
    
    try:
        # Create database if it doesn't exist
        if not database_exists(settings.SQLALCHEMY_DATABASE_URI):
            create_database(settings.SQLALCHEMY_DATABASE_URI)
            logger.info("Database created successfully.")
        
        # Run migrations
        run_migrations()
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Database management commands')
    parser.add_argument('command', choices=['init', 'reset', 'seed', 'reset-and-seed', 'migrate'],
                      help='Command to run: init (create DB and tables), reset (drop and recreate DB), seed (populate with initial data), reset-and-seed (both), or migrate (run migrations)')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            init_database()
        elif args.command == 'reset':
            reset_database("reset")
            run_migrations()
        elif args.command == 'seed':
            run_migrations()  # Ensure schema is up-to-date before seeding
            seed()
        elif args.command == 'reset-and-seed':
            logger.info("Starting reset-and-seed process...")
            reset_database("reset-and-seed")
            logger.info("Database reset completed, running migrations...")
            run_migrations()
            logger.info("Migrations completed, starting seed process...")
            try:
                seed()
                logger.info("Seed process completed successfully")
            except Exception as e:
                logger.error(f"Error during seeding: {str(e)}")
                raise
        elif args.command == 'migrate':
            run_migrations()
            
        logger.info(f"Command '{args.command}' completed successfully.")
        
    except Exception as e:
        logger.error(f"Error executing command '{args.command}': {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 