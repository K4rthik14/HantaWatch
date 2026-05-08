"""Pytest configuration and shared fixtures for MATM backend tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import app


# ── Settings override ─────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Return a test-scoped Settings instance with safe in-memory defaults."""
    return Settings(
        APP_ENV="dev",
        DEBUG=True,
        DATABASE_URL="postgresql+asyncpg://matm:matm@localhost:5432/matm_test",
        CHROMA_HOST="localhost",
        CHROMA_PORT=8001,
        SECRET_KEY="test-secret-key-not-for-production",
    )


@pytest.fixture(autouse=True, scope="session")
def override_settings(test_settings: Settings) -> None:
    """Override the settings dependency for the entire test session."""
    app.dependency_overrides[get_settings] = lambda: test_settings


# ── HTTP client ───────────────────────────────────────────────────────────────


@pytest.fixture
async def client() -> AsyncClient:
    """Yield an async HTTPX test client wired to the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
