"""ORM model — DiseaseEvent.

Central fact table of the surveillance pipeline.  Every signal detected
from any source (WHO, ProMED, scraper, manual entry) lands here as a row.
The ``location`` JSON column stores a GeoJSON-like object so we can later
add PostGIS without a column migration.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class DiseaseEvent(UUIDMixin, Base):
    """A discrete outbreak / case cluster event detected by an ingestion agent."""

    __tablename__ = "disease_events"

    # ── Source linkage ────────────────────────────────────────────────────────
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="The DataSource this event was ingested from (nullable for manual entries).",
    )

    # ── Core epidemiological fields ───────────────────────────────────────────
    disease: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Disease name, e.g. 'Hantavirus Pulmonary Syndrome'.",
    )
    location: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment=(
            "GeoJSON-compatible location object: "
            "{country, region, lat?, lon?, admin_level}."
        ),
    )
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="When the event was reported by the original source.",
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When the event was first written to the database.",
    )

    # ── Epidemiological counts ────────────────────────────────────────────────
    case_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Confirmed or suspected case count, if reported.",
    )
    deaths: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Death count attributed to this event, if reported.",
    )

    # ── Classification ────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="suspected",
        comment="Verification status: confirmed | suspected | rumor.",
    )
    severity: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="low",
        comment="Assessed severity tier: low | medium | high | critical.",
    )

    # ── Raw content & traceability ────────────────────────────────────────────
    raw_content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Full raw text of the source article / report.",
    )
    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Canonical URL of the original report.",
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata",           # actual DB column name
        JSON,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="Arbitrary extra fields (tags, author, language, etc.).",
    )

    # ── Vector store reference ────────────────────────────────────────────────
    vector_id: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="ChromaDB document ID for the embedded representation of this event.",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    source: Mapped["DataSource"] = relationship(  # noqa: F821
        "DataSource",
        back_populates="events",
        lazy="raise",
    )
    risk_scores: Mapped[list["RiskScore"]] = relationship(  # noqa: F821
        "RiskScore",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    alert_logs: Mapped[list["AlertLog"]] = relationship(  # noqa: F821
        "AlertLog",
        back_populates="event",
        lazy="raise",
    )

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_disease_events_disease_reported_at", "disease", "reported_at"),
        Index(
            "ix_disease_events_location_gin",
            "location",
            postgresql_using="gin",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<DiseaseEvent disease={self.disease!r} "
            f"status={self.status!r} severity={self.severity!r}>"
        )
