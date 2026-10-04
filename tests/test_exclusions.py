"""Structural enforcement tests for the Via Vitae capability exclusions."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from viavitae_hermes.security.exclusions import (
    FORBIDDEN_CAPABILITIES,
    FORBIDDEN_MODULE_ROOTS,
    ForbiddenCapabilityError,
    assert_capability_permitted,
)

_SRC_DIR = Path(__file__).resolve().parents[1] / "src" / "viavitae_hermes"
_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+([A-Za-z0-9_.]+)", re.MULTILINE)


def _python_files() -> list[Path]:
    return sorted(_SRC_DIR.rglob("*.py"))


def test_forbidden_capabilities_are_rejected() -> None:
    for capability in FORBIDDEN_CAPABILITIES:
        with pytest.raises(ForbiddenCapabilityError):
            assert_capability_permitted(capability)


def test_permitted_capability_is_allowed() -> None:
    # A read-only, in-boundary capability must not raise.
    assert_capability_permitted("read_only_retrieval")


def test_no_forbidden_module_is_imported_anywhere_in_app() -> None:
    offenders: list[str] = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        for match in _IMPORT_RE.finditer(text):
            root = match.group(1).split(".")[0]
            if root in FORBIDDEN_MODULE_ROOTS:
                offenders.append(f"{path.name}: {root}")
    assert offenders == []
