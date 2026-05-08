"""Pydantic v2 schemas for AlertRule and AlertLog API layer."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ── AlertRule ─────────────────────────────────────────────────────────────────


class AlertRuleCreate(BaseModel):
    """Payload for creating a new AlertRule."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, description="Unique human-readable rule name.")
    disease: str | None = Field(
        None,
        description="Scope this rule to a specific disease. NULL matches any.",
    )
    condition: dict[str, Any] = Field(
        ...,
        description=(
            "Structured condition: "
            "{severity_gte?: str, score_gte?: float, status_in?: list[str], region_in?: list[str]}."
        ),
    )
    channels: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="One or more notification channel configs.",
    )
    is_active: bool = Field(True, description="Whether this rule is evaluated by the engine.")


class AlertRuleResponse(BaseModel):
    """Full AlertRule representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    disease: str | None
    condition: dict[str, Any]
    channels: list[dict[str, Any]]
    is_active: bool
    created_at: datetime


# ── AlertLog ──────────────────────────────────────────────────────────────────


class AlertLogResponse(BaseModel):
    """Audit record of a single alert dispatch attempt."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rule_id: uuid.UUID
    event_id: uuid.UUID
    dispatched_at: datetime
    channel: str
    status: Literal["sent", "failed", "suppressed"]
