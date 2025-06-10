from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Convert PostgresDsn to string for SQLAlchemy
database_url = str(settings.SQLALCHEMY_DATABASE_URI)
logger.info(f"Connecting to database: {database_url}")

# Create SQLAlchemy engine with pool settings
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=True  # Enable SQL query logging for debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit the transaction
    except Exception as e:
        db.rollback()  # Rollback on error
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close() 