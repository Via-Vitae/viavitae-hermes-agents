"""Draft Response Agent — produces drafts only; never sends.

The output is inert data. This agent has no network client and no send/dispatch
method; delivery is a human action performed outside this estate.
"""

from __future__ import annotations

from app.contracts.artifacts import CaseSummary, DraftResponse
from app.contracts.cases import Case


class DraftResponseAgent:
    """Generates a draft reply for human review. Cannot transmit anything."""

    name: str = "draft-response-agent"

    def draft(self, case: Case, summary: CaseSummary) -> DraftResponse:
        body = f"[DRAFT - NOT SENT] Response for case {case.case_id}:\n{summary.text}"
        return DraftResponse(case_id=case.case_id, body=body)
