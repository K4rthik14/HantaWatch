"""Async SQLAlchemy engine and session factory.

Usage in route handlers via ``core/dependencies.py``::

    async def my_route(db: DbSession) -> ...:
        result = await db.execute(select(DiseaseEvent))
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_settings = get_settings()

# ── Engine ────────────────────────────────────────────────────────────────────

engine = create_async_engine(
    _settings.DATABASE_URL,
    pool_pre_ping=True,       # verify connection aliveness before using from pool
    pool_size=10,
    max_overflow=20,
    echo=_settings.DEBUG,     # log SQL only in debug mode
)

# ── Session factory ───────────────────────────────────────────────────────────

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # avoid implicit lazy-loads after commit in async context
    autocommit=False,
    autoflush=False,
)


# ── Dependency ────────────────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an ``AsyncSession`` and guarantee it is closed on exit.

    Use as a FastAPI dependency::

        @router.get("/events")
        async def list_events(db: DbSession) -> list[DiseaseEventResponse]:
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
