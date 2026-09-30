"""Audit Agent — records every decision and data access, append-only."""

from __future__ import annotations

from viavitae_hermes.audit.stream import AuditStream
from viavitae_hermes.contracts.audit import AuditEvent, AuditEventType


class AuditAgent:
    """Writes immutable audit events to a tamper-evident stream."""

    name: str = "audit-agent"

    def __init__(self, stream: AuditStream) -> None:
        self._stream = stream

    @property
    def stream(self) -> AuditStream:
        return self._stream

    def record(
        self, *, event_type: AuditEventType, case_id: str, actor: str, detail: str
    ) -> AuditEvent:
        event = AuditEvent(event_type=event_type, case_id=case_id, actor=actor, detail=detail)
        self._stream.append(event)
        return event
