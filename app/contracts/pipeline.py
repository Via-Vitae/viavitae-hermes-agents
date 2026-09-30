"""Pipeline result contracts for the orchestrator."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.contracts.artifacts import CaseSummary, DraftResponse, SafeguardingAssessment
from app.contracts.consent import ConsentState
from app.contracts.review import ReviewOutcome


class PipelineStatus(StrEnum):
    """Terminal or pending state of a supervised pipeline run.

    There is deliberately no ``SENT`` state: this estate never communicates
    externally on its own.
    """

    HALTED_NO_CONSENT = "halted_no_consent"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    ESCALATED = "escalated"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_INFO = "needs_info"


class PipelineResult(BaseModel):
    """The immutable outcome of processing one case."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    status: PipelineStatus
    consent: ConsentState | None = None
    summary: CaseSummary | None = None
    draft: DraftResponse | None = None
    safeguarding: SafeguardingAssessment | None = None
    review: ReviewOutcome | None = None
