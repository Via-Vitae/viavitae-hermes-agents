"""Audit event contracts for the append-only, tamper-evident trail."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class AuditEventType(StrEnum):
    """Every decision and data access that must be recorded."""

    INTAKE = "intake"
    CLASSIFICATION = "classification"
    CONSENT_CHECK = "consent_check"
    RETRIEVAL = "retrieval"
    SUMMARY = "summary"
    DRAFT = "draft"
    SAFEGUARDING = "safeguarding"
    HUMAN_REVIEW = "human_review"
    BOUNDARY_DENIAL = "boundary_denial"
    HALT = "halt"


class AuditEvent(BaseModel):
    """An immutable record of a single auditable action."""

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(default_factory=lambda: uuid4().hex)
    event_type: AuditEventType
    case_id: str
    actor: str
    detail: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
