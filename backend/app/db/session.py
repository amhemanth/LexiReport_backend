from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings

settings = get_settings()

# Convert PostgresDsn to string for SQLAlchemy
database_url = str(settings.SQLALCHEMY_DATABASE_URI)

# Create SQLAlchemy engine with pool settings
engine = create_engine(database_url, pool_pre_ping=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 