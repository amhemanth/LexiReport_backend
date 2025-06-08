"""
Alembic environment configuration.
This module handles database migrations and seeding.
"""

import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings
from app.db.base import Base  # Import from base.py which has all models
from app.db.base import *  # Import all models
from app.models import *  # Import all models from models package
from app.db.seed import seed_database  # Import seed function

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get settings from our application
settings = get_settings()

def create_database_if_not_exists():
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT,
            database='postgres'  # Connect to default postgres database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.POSTGRES_DB,))
            exists = cursor.fetchone()
            
            if not exists:
                # Create database
                cursor.execute(f'CREATE DATABASE {settings.POSTGRES_DB}')
                print(f"Database {settings.POSTGRES_DB} created successfully")
            else:
                print(f"Database {settings.POSTGRES_DB} already exists")
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {str(e)}")
        print(f"Connection details: host={settings.POSTGRES_SERVER}, user={settings.POSTGRES_USER}, port={settings.POSTGRES_PORT}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

# Create database if it doesn't exist
create_database_if_not_exists()

# Set the database URL in the alembic.ini file
config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = str(settings.SQLALCHEMY_DATABASE_URI)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = str(settings.SQLALCHEMY_DATABASE_URI)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
            
            # Seed the database after migrations
            if context.get_x_argument(as_dictionary=True).get('seed', 'false').lower() == 'true':
                from app.db.session import SessionLocal
                db = SessionLocal()
                try:
                    seed_database(db)
                finally:
                    db.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 