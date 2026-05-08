"""ORM model — IntelligenceBriefing.

Stores LLM-generated intelligence summaries that synthesise multiple
DiseaseEvents into a single human-readable report for a given disease
and time window.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDMixin


class IntelligenceBriefing(UUIDMixin, Base):
    """A synthesised intelligence report produced by the briefing agent."""

    __tablename__ = "intelligence_briefings"

    # ── Scope ─────────────────────────────────────────────────────────────────
    disease: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
        comment="Disease this briefing covers, e.g. 'Hantavirus'.",
    )
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Start of the observation window for events included in this briefing.",
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="End of the observation window.",
    )

    # ── Generated content ─────────────────────────────────────────────────────
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Full Markdown briefing text produced by the LLM.",
    )
    sources_used: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        comment="List of DiseaseEvent UUIDs (as strings) included in this briefing.",
    )
    llm_model: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Exact model identifier used for generation, e.g. 'qwen2.5:7b'.",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the LLM generation completed.",
    )

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="draft",
        server_default="draft",
        comment="Publication state: draft | published | archived.",
    )

    def __repr__(self) -> str:
        return (
            f"<IntelligenceBriefing disease={self.disease!r} "
            f"status={self.status!r}>"
        )
