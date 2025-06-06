"""Database management script."""
import argparse
from app.db.scripts.reset_db import reset_database
from app.db.scripts.seed_db import seed
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
from app.config.config import settings
from app.db.base_class import Base
from app.db.session import engine

def init_database():
    """Initialize the database."""
    # Create database if it doesn't exist
    if not database_exists(settings.SQLALCHEMY_DATABASE_URI):
        create_database(settings.SQLALCHEMY_DATABASE_URI)
        print("Database created successfully.")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def main():
    parser = argparse.ArgumentParser(description='Database management commands')
    parser.add_argument('command', choices=['reset', 'seed', 'reset-and-seed'],
                      help='Command to run: reset (drop and recreate DB), seed (populate with initial data), or reset-and-seed (both)')
    
    args = parser.parse_args()
    
    if args.command == 'reset':
        reset_database("reset")
    elif args.command == 'seed':
        seed()
    elif args.command == 'reset-and-seed':
        reset_database("reset-and-seed")
        seed()

if __name__ == '__main__':
    init_database()
    main() 