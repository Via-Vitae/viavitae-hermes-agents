"""Append-only, tamper-evident audit stream.

Events are hash-chained: each stored link binds an event to its predecessor via
SHA-256. The stream exposes no removal or in-place mutation API. Any rewrite of
the backing records breaks the chain and is detected on the next verify/append,
which refuses to extend a corrupted history.
"""

from __future__ import annotations

import hashlib

from app.contracts.audit import AuditEvent

_GENESIS = ""
_SEPARATOR = "\x1f"


class AuditTamperError(RuntimeError):
    """Raised when the audit hash chain fails verification."""


def _link_hash(previous: str, event: AuditEvent) -> str:
    payload = f"{previous}{_SEPARATOR}{event.model_dump_json()}".encode()
    return hashlib.sha256(payload).hexdigest()


class AuditStream:
    """A hash-chained, append-only sequence of audit events."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._chain: list[str] = []

    def append(self, event: AuditEvent) -> str:
        """Append an event, returning its chain hash.

        Refuses to extend a history that does not verify.
        """
        if not self.verify_chain():
            msg = "audit hash chain failed verification; refusing to append"
            raise AuditTamperError(msg)
        previous = self._chain[-1] if self._chain else _GENESIS
        link = _link_hash(previous, event)
        self._events.append(event)
        self._chain.append(link)
        return link

    def events(self) -> tuple[AuditEvent, ...]:
        """Return an immutable snapshot of recorded events."""
        return tuple(self._events)

    def verify_chain(self) -> bool:
        """Return True only if every link matches its recorded event."""
        previous = _GENESIS
        for event, expected in zip(self._events, self._chain, strict=True):
            computed = _link_hash(previous, event)
            if computed != expected:
                return False
            previous = expected
        return True

    def __len__(self) -> int:
        return len(self._events)
