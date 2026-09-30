"""Information Retrieval Agent — read-only, boundary-scoped retrieval.

Retrieval runs against an injected read-only source. There is no generic
database access and no external egress: the default source returns nothing, and
the guard re-asserts estate isolation on every call.
"""

from __future__ import annotations

from typing import Protocol

from viavitae_hermes.contracts.artifacts import RetrievalResult, RetrievedDocument
from viavitae_hermes.contracts.cases import Case
from viavitae_hermes.security.boundary import BoundaryGuard


class RetrievalSource(Protocol):
    """A read-only document source confined to the Via Vitae boundary."""

    def fetch(self, query: str) -> tuple[RetrievedDocument, ...]: ...


class NullRetrievalSource:
    """Read-only source returning no documents (isolated-estate default)."""

    def fetch(self, query: str) -> tuple[RetrievedDocument, ...]:
        return ()


class InformationRetrievalAgent:
    """Retrieves in-boundary documents; never writes, never leaves the estate."""

    name: str = "retrieval-agent"

    def __init__(self, source: RetrievalSource, guard: BoundaryGuard) -> None:
        self._source = source
        self._guard = guard

    def retrieve(self, case: Case) -> RetrievalResult:
        self._guard.verify_isolation()
        documents = self._source.fetch(case.subject)
        return RetrievalResult(case_id=case.case_id, documents=documents)
