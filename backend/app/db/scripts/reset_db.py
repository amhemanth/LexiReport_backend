"""Database reset script."""
import logging
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from alembic.config import Config
from alembic import command
from app.config.settings import get_settings
from app.db.scripts.seed_db import seed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database(param: str = "reset") -> None:
    """Reset the database by dropping and recreating it."""
    settings = get_settings()
    
    # Connect to postgres database
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Terminate all connections to the database
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{settings.POSTGRES_DB}'
                AND pid <> pg_backend_pid();
            """)
            
            logger.info(f"Terminated existing connections to {settings.POSTGRES_DB}")
            
            # Drop the database if it exists
            cursor.execute(f"DROP DATABASE IF EXISTS {settings.POSTGRES_DB}")
            logger.info(f"Database {settings.POSTGRES_DB} dropped successfully")
            
            # Create a new database
            cursor.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
            logger.info(f"Database {settings.POSTGRES_DB} created successfully")
            
    except Exception as e:
        logger.error("An error occurred while resetting the database:")
        if "cannot drop the currently open database" in str(e):
            logger.error(f"Cannot drop the currently open database {settings.POSTGRES_DB}.")
        logger.error(f"Error: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

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
    if param == "reset-and-seed":
        try:
            logger.info("Starting database seeding process...")
            logger.info(f"Database settings: {settings.SQLALCHEMY_DATABASE_URI}")
            # Import and call seed function directly
            from app.db.scripts.seed_db import seed
            logger.info("Calling seed function...")
            seed()
            logger.info("Database seeded with initial data.")
        except Exception as e:
            logger.error(f"Error during database seeding: {str(e)}")
            logger.error("Stack trace:", exc_info=True)
            raise

if __name__ == "__main__":
    try:
        reset_database()
    except Exception as e:
        logger.error(f"Error in reset_database: {str(e)}")
        sys.exit(1) 