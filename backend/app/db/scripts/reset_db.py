import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, backend_dir)

import psycopg2
from app.config.settings import get_settings
from app.db.scripts.seed_db import seed

def reset_database(param: str = "reset") -> None:
    """Reset the database by dropping and recreating it."""
    settings = get_settings()
    
    # Connect to postgres database
    conn = psycopg2.connect(
        host=settings.POSTGRES_SERVER,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB  
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    try:
        with conn.cursor() as cursor:
            # Terminate all connections to the database
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{settings.POSTGRES_DB}'
                AND pid <> pg_backend_pid();
            """)
            
            print(f"Terminated existing connections to {settings.POSTGRES_DB}")
            
            # Drop the database if it exists
            cursor.execute(f"DROP DATABASE IF EXISTS {settings.POSTGRES_DB}")
            print(f"Database {settings.POSTGRES_DB} dropped successfully")
            
            # Create a new database
            cursor.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
            print(f"Database {settings.POSTGRES_DB} created successfully")
            
    except Exception as e:
        print("An error occurred while resetting the database:")
        if "cannot drop the currently open database" in str(e):
            print(f"Cannot drop the currently open database {settings.POSTGRES_DB}.")
        print(f"Error: {str(e)}")
        raise
    finally:
        conn.close()

    print("Database reset complete.")
    if param == "reset-and-seed":      
        seed()  # Seed the database with initial data
        print("Database seeded with initial data.")
    print(f"Tables created in {settings.POSTGRES_DB}")

if __name__ == "__main__":
    reset_database() 