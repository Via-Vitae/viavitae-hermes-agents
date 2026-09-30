"""Contract tests for the Via Vitae data boundary (config + guard).

These are RED-first TDD tests: the modules under test do not exist yet.
"""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from viavitae_hermes.config import BoundarySettings
from viavitae_hermes.security.boundary import BoundaryGuard, BoundaryViolationError


def _settings(**overrides: object) -> BoundarySettings:
    base: dict[str, object] = {
        "database_dsn": SecretStr("postgresql+psycopg://via:secret@localhost:5432/viavitae"),
        "vector_index_id": "viavitae-cases-v1",
        "kms_key_id": "arn:kms:eu-west-1:000000000000:key/viavitae",
        "checkpoint_namespace": "viavitae",
        "audit_stream_id": "viavitae-audit",
        "secrets_ref": SecretStr("vault:viavitae"),
        "deployment_identity": "sp-viavitae-hermes",
    }
    base.update(overrides)
    return BoundarySettings(**base)  # type: ignore[arg-type]


def test_boundary_settings_requires_every_isolation_control() -> None:
    # Missing the separate KMS key must fail closed at construction time.
    with pytest.raises(ValidationError):
        BoundarySettings(  # type: ignore[call-arg]
            database_dsn=SecretStr("postgresql+psycopg://x"),
            vector_index_id="viavitae-cases-v1",
            checkpoint_namespace="viavitae",
            audit_stream_id="viavitae-audit",
            secrets_ref=SecretStr("vault:viavitae"),
            deployment_identity="sp-viavitae-hermes",
        )


def test_boundary_settings_rejects_shared_jol_identifiers() -> None:
    # No control may reference the JOL estate (no shared memory / identity).
    with pytest.raises(ValidationError):
        _settings(checkpoint_namespace="jol-shared")


def test_boundary_settings_rejects_non_viavitae_estate() -> None:
    with pytest.raises(ValidationError):
        _settings(estate="jol")  # type: ignore[typeddict-item]


def test_guard_egress_is_denied_by_default() -> None:
    guard = BoundaryGuard(_settings())
    with pytest.raises(BoundaryViolationError):
        guard.assert_no_external_egress("https://api.example.com")


def test_guard_rejects_cross_estate_target() -> None:
    guard = BoundaryGuard(_settings())
    with pytest.raises(BoundaryViolationError):
        guard.assert_no_external_egress("jol://internal/memory")


def test_guard_verify_passes_for_isolated_settings() -> None:
    guard = BoundaryGuard(_settings())
    # Isolated, Viavitae-only settings must verify without raising.
    guard.verify_isolation()
