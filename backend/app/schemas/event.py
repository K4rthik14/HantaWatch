"""Pydantic v2 schemas for DiseaseEvent API layer."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import LocationSchema, SourceSummary


# ── Write schemas ─────────────────────────────────────────────────────────────


class DiseaseEventCreate(BaseModel):
    """Payload for creating a new DiseaseEvent via the API or ingestion agent."""

    model_config = ConfigDict(from_attributes=True)

    source_id: uuid.UUID | None = Field(
        None,
        description="UUID of the DataSource. Omit for manual entries.",
    )
    disease: str = Field(..., min_length=1, description="Disease name.")
    location: LocationSchema = Field(..., description="GeoJSON-compatible location.")
    reported_at: datetime = Field(..., description="When the event was reported.")
    case_count: int | None = Field(None, ge=0, description="Number of reported cases.")
    deaths: int | None = Field(None, ge=0, description="Number of reported deaths.")
    status: Literal["confirmed", "suspected", "rumor"] = Field(
        "suspected",
        description="Verification status of the event.",
    )
    severity: Literal["low", "medium", "high", "critical"] = Field(
        "low",
        description="Initial assessed severity.",
    )
    raw_content: str | None = Field(None, description="Full source article text.")
    source_url: str | None = Field(None, description="Canonical URL of the source.")
    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        alias="metadata",
        description="Arbitrary additional fields.",
    )


# ── Read schemas ──────────────────────────────────────────────────────────────


class DiseaseEventResponse(BaseModel):
    """Full DiseaseEvent representation returned by the API."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    disease: str
    location: dict[str, Any]
    reported_at: datetime
    ingested_at: datetime
    case_count: int | None
    deaths: int | None
    status: str
    severity: str
    source_url: str | None
    vector_id: str | None
    metadata_: dict[str, Any] = Field(alias="metadata", default_factory=dict)

    # Enrichment — populated by the route layer via a joined query
    risk_score: float | None = Field(
        None,
        description="Latest aggregate risk score (0–100), if computed.",
    )
    source: SourceSummary | None = Field(
        None,
        description="Lightweight source info, if the event has a linked source.",
    )
