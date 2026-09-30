"""Case Summary Agent — bounded, source-attributed summaries for humans."""

from __future__ import annotations

from viavitae_hermes.contracts.artifacts import CaseSummary, RetrievalResult
from viavitae_hermes.contracts.cases import Case

_MAX_SUMMARY_CHARS = 1200


class CaseSummaryAgent:
    """Produces a length-bounded summary that cites its sources."""

    name: str = "summary-agent"

    def summarize(self, case: Case, retrieval: RetrievalResult) -> CaseSummary:
        source_ids = tuple(document.doc_id for document in retrieval.documents)
        narrative = f"Case {case.case_id} concerning {case.subject}."
        truncated = len(narrative) > _MAX_SUMMARY_CHARS
        return CaseSummary(
            case_id=case.case_id,
            text=narrative[:_MAX_SUMMARY_CHARS],
            source_ids=source_ids,
            truncated=truncated,
        )
