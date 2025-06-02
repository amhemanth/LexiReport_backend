import app.models  # Ensure all models are registered

from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.password import get_password_hash
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
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
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Open a new session after tables are created
        db = SessionLocal()
        create_test_user(db)
        db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db()