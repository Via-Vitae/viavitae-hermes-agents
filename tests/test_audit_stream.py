"""Contract tests for the tamper-evident, append-only audit stream.

This module is now implemented at viavitae_hermes.audit.stream; originally RED-first.
"""

from __future__ import annotations

import pytest

from viavitae_hermes.audit.stream import AuditStream, AuditTamperError
from viavitae_hermes.contracts.audit import AuditEvent, AuditEventType


def _event(case_id: str = "c1", detail: str = "x") -> AuditEvent:
    return AuditEvent(
        event_type=AuditEventType.INTAKE,
        case_id=case_id,
        actor="intake-agent",
        detail=detail,
    )


def test_append_records_events_in_order() -> None:
    stream = AuditStream()
    stream.append(_event(detail="first"))
    stream.append(_event(detail="second"))
    assert [event.detail for event in stream.events()] == ["first", "second"]
    assert len(stream) == 2


def test_chain_verifies_when_untampered() -> None:
    stream = AuditStream()
    stream.append(_event(detail="a"))
    stream.append(_event(detail="b"))
    assert stream.verify_chain() is True


def test_tampering_with_a_recorded_event_is_detected() -> None:
    stream = AuditStream()
    stream.append(_event(detail="original"))
    # Simulate an attacker rewriting history in the backing store.
    stream._events[0] = _event(detail="altered")
    assert stream.verify_chain() is False
    with pytest.raises(AuditTamperError):
        stream.append(_event(detail="next"))


def test_stream_exposes_no_removal_api() -> None:
    stream = AuditStream()
    for forbidden in ("pop", "remove", "delete", "clear", "__delitem__", "__setitem__"):
        assert not hasattr(stream, forbidden), f"audit stream must not expose {forbidden}"


def test_events_returns_immutable_view() -> None:
    stream = AuditStream()
    stream.append(_event())
    events = stream.events()
    assert isinstance(events, tuple)
