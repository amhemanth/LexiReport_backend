import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, backend_dir)

# Load test environment variables
load_dotenv(os.path.join(backend_dir, ".env.test"))

def create_test_database():
    """Create test database if it doesn't exist."""
    # Get database configuration from environment variables
    db_name = os.getenv("POSTGRES_DB", "test_lexireport")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_SERVER", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating test database: {db_name}")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print("Test database created successfully")
        else:
            print(f"Test database {db_name} already exists")

    except Exception as e:
        print(f"Error creating test database: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def setup_test_db():
    """Set up test database and seed initial data."""
    try:
        # Create test database if it doesn't exist
        create_test_database()
        
        # Import and run reset and seed functions
        from app.db.scripts.test_reset_db import main as reset_test_db
        from app.db.scripts.test_seed_db import seed as seed_test_db
        
        # Reset and seed the database
        print("Resetting test database...")
        reset_test_db()
        print("Seeding test database...")
        seed_test_db()
        print("Test database setup completed successfully")
        
    except Exception as e:
        print(f"Error setting up test database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_test_db() 