"""Read-only artifacts produced by assistive agents.

None of these models can perform I/O. A draft is inert data, never a delivery
action; sending is a human act performed outside this estate.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class RetrievedDocument(BaseModel):
    """A single read-only document returned within the data boundary."""

    model_config = ConfigDict(frozen=True)

    doc_id: str
    text: str
    origin: str


class RetrievalResult(BaseModel):
    """The bounded set of documents retrieved for a case."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    documents: tuple[RetrievedDocument, ...] = ()


class CaseSummary(BaseModel):
    """A bounded, source-attributed summary prepared for human review."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    text: str
    source_ids: tuple[str, ...] = ()
    truncated: bool = False


class DraftResponse(BaseModel):
    """A draft reply. Structurally incapable of being sent."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    body: str
    is_draft: Literal[True] = True


class SafeguardingAssessment(BaseModel):
    """An immutable safeguarding assessment; escalation cannot be suppressed."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    escalated: bool
    triggers: tuple[str, ...] = ()
    alert: str | None = None
