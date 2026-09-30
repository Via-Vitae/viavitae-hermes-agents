"""Safeguarding Escalation Agent — raises protected alerts to a human.

An escalation cannot be suppressed by any other agent: the assessment is
immutable and the orchestrator must surface it regardless of other outcomes.
"""

from __future__ import annotations

from app.contracts.artifacts import CaseSummary, SafeguardingAssessment
from app.contracts.cases import Case

_ESCALATION_TOKENS = frozenset(
    {
        "harm",
        "suicide",
        "self-harm",
        "abuse",
        "neglect",
        "at risk",
        "threat",
        "danger",
        "safeguarding",
    }
)


class SafeguardingEscalationAgent:
    """Detects risk triggers and raises a protected, non-suppressible alert."""

    name: str = "safeguarding-agent"

    def assess(self, case: Case, summary: CaseSummary) -> SafeguardingAssessment:
        text = f"{case.raw_input} {summary.text}".casefold()
        triggers = tuple(sorted(token for token in _ESCALATION_TOKENS if token in text))
        escalated = bool(triggers)
        alert = (
            f"SAFEGUARDING ALERT case {case.case_id}: triggers={', '.join(triggers)}"
            if escalated
            else None
        )
        return SafeguardingAssessment(
            case_id=case.case_id,
            escalated=escalated,
            triggers=triggers,
            alert=alert,
        )
