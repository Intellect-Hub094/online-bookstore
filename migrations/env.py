# migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add your project directory to the Python path
sys.path.append(os.getcwd())

# Import your Flask app and SQLAlchemy db instance
from app import app
from extensions import db

# Alembic configuration
config = context.config

# Set the SQLAlchemy URL from your Flask app's configuration
config.set_main_option(
    "sqlalchemy.url",
    "postgresql+psycopg2://postgres.ofwhjskhwnxfkrolxnue:ofwhjskhwnxfkrolxnue@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your models' metadata here
target_metadata = db.Model.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()