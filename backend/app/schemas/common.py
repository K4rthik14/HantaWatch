"""Shared / reusable Pydantic v2 schemas used across the MATM API."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ── Pagination ────────────────────────────────────────────────────────────────


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response envelope.

    Example::

        PaginatedResponse[DiseaseEventResponse](
            total=42, page=1, page_size=20, items=[...]
        )
    """

    model_config = ConfigDict(from_attributes=True)

    total: int = Field(..., description="Total number of records matching the query.")
    page: int = Field(1, ge=1, description="Current page number (1-indexed).")
    page_size: int = Field(20, ge=1, le=200, description="Number of items per page.")
    items: list[T] = Field(..., description="Slice of results for the current page.")


# ── Location ──────────────────────────────────────────────────────────────────


class LocationSchema(BaseModel):
    """GeoJSON-compatible location object attached to DiseaseEvent."""

    model_config = ConfigDict(from_attributes=True)

    country: str = Field(..., description="ISO 3166-1 alpha-2 or full country name.")
    region: str | None = Field(None, description="Province / state / oblast.")
    lat: float | None = Field(None, ge=-90, le=90, description="Latitude in decimal degrees.")
    lon: float | None = Field(None, ge=-180, le=180, description="Longitude in decimal degrees.")
    admin_level: str | None = Field(
        None,
        description="Administrative precision: country | region | city.",
    )


# ── Source summary (lightweight, no config/health exposed) ─────────────────────


class SourceSummary(BaseModel):
    """Lightweight DataSource projection — safe to embed in event responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    source_type: str
    is_active: bool
