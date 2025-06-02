import os
import logging
from datetime import datetime, timezone
from sqlalchemy import inspect
from sqlalchemy.orm import Session

# Import all models
from app.models import Base, User, Report, ReportInsight
from app.core.database import engine, SessionLocal
from app.core.password import get_password_hash

logger = logging.getLogger(__name__)

def verify_tables_exist(engine):
    """Verify that all tables exist in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required_tables = ['users', 'reports', 'report_insights']
    missing_tables = [table for table in required_tables if table not in tables]
    if missing_tables:
        raise Exception(f"Missing tables: {missing_tables}")
    return True

def create_test_user(db: Session) -> None:
    try:
        # Check if test user already exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if test_user:
            logger.info("Test user already exists")
            return

        # Create test user
        test_user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(test_user)
        db.commit()
        logger.info("Test user created successfully")
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        db.rollback()
        raise

def init_db() -> None:
    try:
        # Get the absolute path to the database file
        db_path = os.path.abspath("app.db")
        logger.info(f"Database path: {db_path}")

        # Delete existing database file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Deleted existing database file: {db_path}")

        # Create tables
        Base.metadata.drop_all(bind=engine)  # Drop all tables first
        Base.metadata.create_all(bind=engine)  # Create all tables
        logger.info("Database tables created successfully")

        # Verify tables exist
        verify_tables_exist(engine)
        logger.info("Verified all required tables exist")

        # Create a new session after tables are created
        db = SessionLocal()
        try:
            create_test_user(db)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 