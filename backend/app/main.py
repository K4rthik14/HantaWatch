"""MATM FastAPI application entry point."""

from __future__ import annotations

import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

# Initialise logging before anything else so every import sees the configuration
configure_logging()

logger = get_logger(__name__)
settings = get_settings()

# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    if settings.is_production and settings.SECRET_KEY == "change-me-in-production":
        warnings.warn(
            "SECRET_KEY is set to the default placeholder value in production. "
            "This is a security risk — override it with a strong random secret.",
            stacklevel=1,
        )

    logger.info(
        "MATM backend starting",
        env=settings.APP_ENV,
        debug=settings.DEBUG,
        llm_model=settings.LLM_DEFAULT_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
    )

    yield  # ← application runs here

    logger.info("MATM backend shutting down", env=settings.APP_ENV)


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Multi-Agent Threat Monitor (MATM)",
    description=(
        "AI-assisted infectious disease surveillance platform. "
        "Ingests signals from WHO, ProMED, and other public health sources, "
        "then uses a multi-agent pipeline to detect, score, and alert on emerging threats."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ── Middleware ────────────────────────────────────────────────────────────────

_ALLOWED_ORIGINS = (
    ["*"]
    if settings.APP_ENV == "dev"
    else [
        # Add your staging / production frontend origins here
        "https://hantawatch.example.com",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────


@app.get(
    "/health",
    summary="Health check",
    tags=["ops"],
    response_model=dict,
)
async def health() -> dict[str, str]:
    """Return the service liveness status, deployment environment, and API version."""
    return {
        "status": "ok",
        "env": settings.APP_ENV,
        "version": app.version,
    }
