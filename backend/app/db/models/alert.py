"""ORM models — AlertRule and AlertLog.

AlertRule defines *when* to alert (condition) and *how* to alert (channels).
AlertLog records every dispatch attempt so we have a full audit trail.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class AlertRule(UUIDMixin, Base):
    """A user-configured rule that triggers alerts when conditions are met."""

    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        comment="Human-readable rule name, e.g. 'Critical Ebola Alert'.",
    )
    disease: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        index=True,
        comment="If set, the rule only fires for this disease. NULL = any disease.",
    )
    condition: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment=(
            "Structured condition expression: "
            "{severity_gte, score_gte, status_in, region_in, …}."
        ),
    )
    channels: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        comment=(
            "Notification channels to use: "
            "[{type: 'webhook', url: '...'}, {type: 'email', to: '...'}]."
        ),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="Inactive rules are evaluated but produce no dispatches.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ── Relationship ──────────────────────────────────────────────────────────
    logs: Mapped[list["AlertLog"]] = relationship(
        "AlertLog",
        back_populates="rule",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<AlertRule name={self.name!r} active={self.is_active}>"


class AlertLog(UUIDMixin, Base):
    """Immutable audit record of a single alert dispatch attempt."""

    __tablename__ = "alert_log"

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alert_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The AlertRule that triggered this dispatch.",
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("disease_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The DiseaseEvent that matched the rule condition.",
    )
    dispatched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the dispatch was attempted.",
    )
    channel: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Channel type used: webhook | email | slack | …",
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Outcome: sent | failed | suppressed.",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    rule: Mapped["AlertRule"] = relationship(
        "AlertRule",
        back_populates="logs",
        lazy="raise",
    )
    event: Mapped["DiseaseEvent"] = relationship(  # noqa: F821
        "DiseaseEvent",
        back_populates="alert_logs",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<AlertLog rule_id={self.rule_id} status={self.status!r}>"
