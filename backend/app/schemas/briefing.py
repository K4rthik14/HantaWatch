"""Pydantic v2 schemas for IntelligenceBriefing API layer."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas ────────────────────────────────────────────────────────────


class BriefingGenerateRequest(BaseModel):
    """Request body for triggering a new LLM-generated intelligence briefing."""

    model_config = ConfigDict(from_attributes=True)

    disease: str = Field(..., min_length=1, description="Disease to generate a briefing for.")
    period_start: datetime = Field(..., description="Start of the analysis window (UTC).")
    period_end: datetime = Field(..., description="End of the analysis window (UTC).")
    llm_model: str | None = Field(
        None,
        description=(
            "Override the default LLM model for this briefing. "
            "Defaults to settings.LLM_DEFAULT_MODEL."
        ),
    )


# ── Response schemas ───────────────────────────────────────────────────────────


class BriefingResponse(BaseModel):
    """Full IntelligenceBriefing representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    disease: str
    period_start: datetime
    period_end: datetime
    content: str
    sources_used: list[str] = Field(
        description="List of DiseaseEvent UUIDs included in this briefing.",
    )
    llm_model: str
    generated_at: datetime
    status: Literal["draft", "published", "archived"]
