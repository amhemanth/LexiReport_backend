"""Database session management."""
import logging
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from app.config.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Get database settings
settings = get_settings()

# Create engine with connection pooling and timeout settings
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=settings.DB_POOL_SIZE,  # Maximum number of connections to keep
    max_overflow=settings.DB_MAX_OVERFLOW,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=settings.DB_POOL_TIMEOUT,  # Seconds to wait before giving up on getting a connection from the pool
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle connections after specified time
    echo=settings.SQL_ECHO,  # Enable SQL query logging if configured
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    """Log successful database connection."""
    logger.info("Connected to database: %s", settings.SQLALCHEMY_DATABASE_URI)

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout from pool."""
    logger.debug("Checking out database connection from pool")

@event.listens_for(engine, "checkin")
def checkin(dbapi_connection, connection_record):
    """Log connection checkin to pool."""
    logger.debug("Checking in database connection to pool")

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with proper error handling and cleanup.
    
    Yields:
        Session: Database session
        
    Raises:
        SQLAlchemyError: If there's an error with the database session
    """
    db = SessionLocal()
    try:
        logger.debug("Starting database session")
        yield db
        db.commit()
        logger.debug("Committed database session")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database session error: %s", str(e))
        raise
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error in database session: %s", str(e))
        raise
    finally:
        db.close()
        logger.debug("Closed database session")

def get_db_session() -> Session:
    """Get a database session.
    
    Returns:
        Session: Database session
        
    Note:
        This function should be used with FastAPI's dependency injection system.
        For manual session management, use get_db() context manager instead.
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error("Error creating database session: %s", str(e))
        raise

def init_db() -> None:
    """Initialize database connection and verify connectivity."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        raise

def close_db() -> None:
    """Close all database connections."""
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database connections: %s", str(e))
        raise 