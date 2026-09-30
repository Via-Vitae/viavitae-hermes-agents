"""Deny-by-default boundary guard for the Via Vitae estate.

Two structural invariants are enforced here:

* **No external network egress.** This blocks autonomous external communication.
  The initial release has an empty allowlist, so every outbound target is denied.
* **No cross-estate targets.** This blocks any shared JOL memory or data path.

Agents must call :meth:`BoundaryGuard.assert_no_external_egress` before any
outbound operation; because it always raises in the initial release, egress is
structurally impossible rather than merely unused.
"""

from __future__ import annotations

from app.config import BoundarySettings

_ESTATE = "viavitae"
_FORBIDDEN_ESTATE_MARKER = "jol"


class BoundaryViolationError(RuntimeError):
    """Raised when an operation would cross the Via Vitae data boundary."""


class BoundaryGuard:
    """Enforces estate isolation and deny-by-default egress."""

    def __init__(self, settings: BoundarySettings) -> None:
        self._settings = settings

    def verify_isolation(self) -> None:
        """Re-assert that the loaded settings describe an isolated estate."""
        if self._settings.estate != _ESTATE:
            msg = f"Via Vitae must run within its own isolated {_ESTATE!r} estate"
            raise BoundaryViolationError(msg)

    def assert_no_external_egress(self, target: str) -> None:
        """Deny an outbound target. Always raises in the initial release."""
        normalized = target.casefold()
        if _FORBIDDEN_ESTATE_MARKER in normalized:
            msg = f"cross-estate egress denied: {target!r}"
            raise BoundaryViolationError(msg)
        # Deny-by-default: no external communication is permitted initially.
        msg = f"external egress denied by default: {target!r}"
        raise BoundaryViolationError(msg)
