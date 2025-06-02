from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Get absolute path to database file
db_path = os.path.abspath("app.db")
logger.info(f"Database path: {db_path}")

# Create SQLAlchemy engine
engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.DEBUG  # Enable SQL query logging in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        logger.info("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Database session closed")
        db.close() 