"""FastAPI dependency injection providers.

Import these with ``Depends(...)`` in route handlers.
Additional providers (chroma client, etc.) will be added
in subsequent phases.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db

# ── Settings ──────────────────────────────────────────────────────────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]
"""Inject the application settings into a route handler.

Usage::

    @router.get("/example")
    async def example(settings: SettingsDep) -> dict:
        return {"env": settings.APP_ENV}
"""

# ── Database ──────────────────────────────────────────────────────────────────

DbSession = Annotated[AsyncSession, Depends(get_db)]
"""Inject an async SQLAlchemy session into a route handler.

Usage::

    @router.get("/events")
    async def list_events(db: DbSession) -> list[DiseaseEventResponse]:
        ...
"""
