"""Human Review Agent — the mandatory supervision chokepoint.

This agent never auto-approves. Without an explicit, attributable human decision
it fails closed by raising :class:`HumanReviewRequiredError`.
"""

from __future__ import annotations

from viavitae_hermes.contracts.cases import Case
from viavitae_hermes.contracts.review import HumanReviewDecision, ReviewDecision, ReviewOutcome


class HumanReviewRequiredError(RuntimeError):
    """Raised when a case reaches the review gate without a human decision."""


class HumanReviewAgent:
    """Records a human decision; refuses to proceed without one."""

    name: str = "human-review-agent"

    def review(self, case: Case, decision: HumanReviewDecision | None) -> ReviewOutcome:
        if decision is None:
            msg = f"case {case.case_id} requires human review; no autonomous approval"
            raise HumanReviewRequiredError(msg)
        if decision.case_id != case.case_id:
            msg = "human decision does not match the case under review"
            raise HumanReviewRequiredError(msg)
        return ReviewOutcome(
            case_id=case.case_id,
            reviewer_id=decision.reviewer_id,
            decision=decision.decision,
            rationale=decision.rationale,
            approved=decision.decision is ReviewDecision.APPROVED,
        )
