"""Human-review contracts: the mandatory supervision chokepoint."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class ReviewDecision(StrEnum):
    """A human reviewer's explicit decision."""

    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_INFO = "needs_info"


class HumanReviewDecision(BaseModel):
    """An attributable human decision; anonymous or unreasoned input is rejected."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    reviewer_id: str
    decision: ReviewDecision
    rationale: str

    @model_validator(mode="after")
    def _ensure_attributable(self) -> HumanReviewDecision:
        if not self.reviewer_id.strip():
            msg = "reviewer_id is required for accountability"
            raise ValueError(msg)
        if not self.rationale.strip():
            msg = "rationale is required for accountability"
            raise ValueError(msg)
        return self


class ReviewOutcome(BaseModel):
    """The validated outcome recorded at the review gate."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    reviewer_id: str
    decision: ReviewDecision
    rationale: str
    approved: bool
