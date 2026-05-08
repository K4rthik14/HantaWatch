"""ORM model — DataSource.

Tracks every external feed (WHO RSS, ProMED, ECDC, etc.) that the ingestion
agents pull from.  The ``config`` JSON column stores feed-specific parameters
(e.g. polling interval, auth headers) without needing schema migrations for
each new source type.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class DataSource(UUIDMixin, TimestampMixin, Base):
    """An external data source ingested by the surveillance pipeline."""

    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        comment="Human-readable unique name, e.g. 'WHO RSS English'.",
    )
    source_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Ingestion adapter type: rss | scraper | api | manual.",
    )
    config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Feed-specific configuration (URLs, auth, schedule, etc.).",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="Disabled sources are skipped by the scheduler.",
    )
    last_fetched: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of the most recent successful ingestion run.",
    )
    health: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="Latest health metrics: {last_error, consecutive_failures, …}.",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    events: Mapped[list["DiseaseEvent"]] = relationship(  # noqa: F821
        "DiseaseEvent",
        back_populates="source",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<DataSource name={self.name!r} type={self.source_type!r}>"
