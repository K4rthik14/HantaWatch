"""Domain exception hierarchy for MATM.

All custom exceptions inherit from MATMBaseException so callers can
catch the entire domain with a single ``except MATMBaseException`` clause,
or narrow to a specific subdomain.
"""

from __future__ import annotations

from typing import Any


class MATMBaseException(Exception):
    """Root exception for all MATM domain errors.

    Attributes:
        message: Human-readable description of the error.
        detail:  Optional structured payload for logging / API responses.
    """

    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, detail={self.detail!r})"


# ── Ingestion ────────────────────────────────────────────────────────────────

class IngestionError(MATMBaseException):
    """Raised when a data ingestion agent fails to fetch or parse a source.

    Examples: network timeout on WHO RSS feed, malformed XML, duplicate
    article detection failure.
    """


# ── RAG / Vector Store ────────────────────────────────────────────────────────

class RAGError(MATMBaseException):
    """Raised when the retrieval-augmented generation pipeline fails.

    Examples: ChromaDB connection refused, embedding model unavailable,
    empty retrieval result when a non-empty result is required.
    """


# ── Agent ─────────────────────────────────────────────────────────────────────

class AgentError(MATMBaseException):
    """Raised when an AI agent encounters an unrecoverable error.

    Examples: LLM API timeout, malformed JSON tool call, agent loop
    exceeds maximum iterations.
    """


# ── Scoring ───────────────────────────────────────────────────────────────────

class ScoringError(MATMBaseException):
    """Raised when the threat-scoring pipeline produces an invalid result.

    Examples: score out of expected range, missing required signal fields,
    model confidence below threshold.
    """


# ── Alerting ──────────────────────────────────────────────────────────────────

class AlertError(MATMBaseException):
    """Raised when the alerting subsystem fails to dispatch a notification.

    Examples: webhook delivery failure, alert deduplication key collision,
    missing recipient configuration.
    """


# ── Database ──────────────────────────────────────────────────────────────────

class DatabaseError(MATMBaseException):
    """Raised when a database operation fails at the repository layer.

    Examples: connection pool exhausted, constraint violation, migration
    version mismatch detected at startup.
    """
