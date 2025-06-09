"""Database reset script."""
import logging
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from alembic.config import Config
from alembic import command
from app.config.settings import get_settings
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """Reset the database by dropping and recreating all tables."""
    try:
        # Create engine without database name
        engine = create_engine(get_settings().SQLALCHEMY_DATABASE_URI.rsplit('/', 1)[0])
        
        # Connect to postgres database
        with engine.connect() as conn:
            # Terminate all connections to the database
            conn.execute(text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{get_settings().POSTGRES_DB}'
                AND pid <> pg_backend_pid();
            """))
            
            # Drop and recreate database
            conn.execute(text("COMMIT"))
            conn.execute(text(f"DROP DATABASE IF EXISTS {get_settings().POSTGRES_DB}"))
            conn.execute(text(f"CREATE DATABASE {get_settings().POSTGRES_DB}"))
        
        logging.info("Database reset successfully")
    except Exception as e:
        logging.error(f"Error resetting database: {str(e)}")
        raise

    # Run migrations
    try:
        # Get the path to alembic.ini
        alembic_cfg = Config("alembic.ini")
        # Run all migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise

    logger.info("Database reset complete.")

if __name__ == "__main__":
    try:
        reset_database()
    except Exception as e:
        logger.error(f"Error in reset_database: {str(e)}")
        sys.exit(1) 