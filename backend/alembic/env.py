"""Alembic migration environment for MATM.

Supports async engine (asyncpg / SQLAlchemy asyncio) with autogenerate
from the full ORM model graph.

Run::

    # Apply all pending migrations
    alembic upgrade head

    # Generate a new auto-migration
    alembic revision --autogenerate -m "describe change"
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Import Base and every model so autogenerate can see all tables ────────────
from app.db.base import Base
import app.db.models  # noqa: F401 — side-effect import registers all models

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# Read DATABASE_URL from the environment; override the ini placeholder.
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Set up Python stdlib logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate target
target_metadata = Base.metadata


# ── Offline mode (generate SQL script without a live DB connection) ───────────


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — outputs raw SQL."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (run against a live async engine) ────────────────────────────


def do_run_migrations(connection: object) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations inside a sync wrapper."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ───────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
