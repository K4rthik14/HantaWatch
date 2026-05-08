"""ORM model — RiskScore.

Stores the output of the threat-scoring agent for a given DiseaseEvent.
Multiple scoring runs may exist per event (model upgrades, re-scoring).
The ``breakdown`` JSON column captures per-factor contributions so the
frontend can render a transparent score explanation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class RiskScore(UUIDMixin, Base):
    """Threat-scoring agent output for a single DiseaseEvent."""

    __tablename__ = "risk_scores"

    # ── Event linkage (cascade-delete so scores disappear with their event) ──
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("disease_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The DiseaseEvent this score was computed for.",
    )

    # ── Score ─────────────────────────────────────────────────────────────────
    score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Aggregate threat score in [0.00, 100.00].",
    )
    breakdown: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment=(
            "Per-factor contributions: "
            "{severity_weight, spread_rate, novelty, data_quality, …}."
        ),
    )
    model_ver: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Scoring model version string, e.g. 'v1.0.0' or a git SHA.",
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when this score was computed.",
    )

    # ── Relationship ──────────────────────────────────────────────────────────
    event: Mapped["DiseaseEvent"] = relationship(  # noqa: F821
        "DiseaseEvent",
        back_populates="risk_scores",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<RiskScore event_id={self.event_id} score={self.score} ver={self.model_ver!r}>"
