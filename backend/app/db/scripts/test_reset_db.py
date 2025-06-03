import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, backend_dir)

import psycopg2
from sqlalchemy import create_engine
from app.config.settings import get_settings
from app.db.base import create_tables

def main():
    """Reset the test database by dropping and recreating it."""
    settings = get_settings()
    
    # Use test database name
    test_db_name = 'test_lexireport'
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    host = settings.POSTGRES_SERVER
    port = settings.POSTGRES_PORT
    default_db = 'postgres'

    # Connect to default db to drop/create test db
    conn = psycopg2.connect(
        dbname=default_db,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Terminate connections
        cur.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{test_db_name}'
            AND pid <> pg_backend_pid();
        """)
        print(f"Terminated existing connections to {test_db_name}")
        
        # Drop db
        cur.execute(f"DROP DATABASE IF EXISTS {test_db_name};")
        print(f"Database {test_db_name} dropped successfully")
        
        # Create db
        cur.execute(f"CREATE DATABASE {test_db_name};")
        print(f"Database {test_db_name} created successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

    # Create tables
    test_db_url = f"postgresql://{user}:{password}@{host}:{port}/{test_db_name}"
    engine = create_engine(test_db_url)
    create_tables(engine)
    print(f"Tables created in {test_db_name}")

if __name__ == "__main__":
    main() 