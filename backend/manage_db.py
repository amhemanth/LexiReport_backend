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
from app.db.scripts.seed_db import seed as seed_database
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
        
        # Set the database URL in the alembic.ini file
        settings = get_settings()
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))
        
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
        db_url = str(settings.SQLALCHEMY_DATABASE_URI)
        if not database_exists(db_url):
            create_database(db_url)
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
            reset_database()
            run_migrations()
        elif args.command == 'seed':
            run_migrations()  # Ensure schema is up-to-date before seeding
            seed_database()
        elif args.command == 'reset-and-seed':
            logger.info("Starting reset-and-seed process...")
            try:
                # First reset the database
                reset_database()
                logger.info("Database reset completed, running migrations...")
                
                # Then run migrations
                run_migrations()
                logger.info("Migrations completed, starting seed process...")
                
                # Finally seed the database
                seed_database()
                logger.info("Seed process completed successfully")
            except Exception as e:
                logger.error(f"Error during reset-and-seed process: {str(e)}")
                logger.error("Stack trace:", exc_info=True)
                raise
        elif args.command == 'migrate':
            run_migrations()
            
        logger.info(f"Command '{args.command}' completed successfully.")
        
    except Exception as e:
        logger.error(f"Error executing command '{args.command}': {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 