"""FastAPI dependency injection providers.

Import these with ``Depends(...)`` in route handlers.
Additional providers (db session, chroma client, etc.) will be added
in subsequent phases.
"""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings

# ── Settings ──────────────────────────────────────────────────────────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]
"""Inject the application settings into a route handler.

Usage::

    @router.get("/example")
    async def example(settings: SettingsDep) -> dict:
        return {"env": settings.APP_ENV}
"""
