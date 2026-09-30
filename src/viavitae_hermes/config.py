"""Via Vitae data-boundary configuration.

Fail-closed by construction: every isolation control is required, no secret has
a default, and any value referencing another estate (e.g. the JOL operational
estate) is rejected. Loading incomplete or cross-estate configuration raises
``ValidationError`` rather than degrading to a shared or insecure default.
"""

from __future__ import annotations

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ESTATE = "viavitae"
_FORBIDDEN_ESTATE_MARKER = "jol"


class BoundarySettings(BaseSettings):
    """Separate, non-shared controls defining the Via Vitae data boundary."""

    model_config = SettingsConfigDict(
        env_prefix="VIAVITAE_",
        frozen=True,
        extra="forbid",
    )

    # Deployment identity of this estate; must never be another estate.
    estate: str = _ESTATE

    # Separate database (no generic access; scoped to Via Vitae only).
    database_dsn: SecretStr
    # Separate vector index.
    vector_index_id: str
    # Separate KMS key.
    kms_key_id: str
    # Separate checkpoints namespace.
    checkpoint_namespace: str
    # Separate audit stream identifier.
    audit_stream_id: str
    # Separate secrets reference (never shared with other estates).
    secrets_ref: SecretStr
    # Separate deployment identity (service principal).
    deployment_identity: str

    @model_validator(mode="after")
    def _ensure_isolated_single_estate(self) -> BoundarySettings:
        if self.estate != _ESTATE:
            msg = f"estate must be {_ESTATE!r}, got {self.estate!r}"
            raise ValueError(msg)

        controls = {
            "database_dsn": self.database_dsn.get_secret_value(),
            "vector_index_id": self.vector_index_id,
            "kms_key_id": self.kms_key_id,
            "checkpoint_namespace": self.checkpoint_namespace,
            "audit_stream_id": self.audit_stream_id,
            "secrets_ref": self.secrets_ref.get_secret_value(),
            "deployment_identity": self.deployment_identity,
        }
        for name, value in controls.items():
            if _FORBIDDEN_ESTATE_MARKER in value.casefold():
                msg = (
                    f"Via Vitae boundary control {name!r} must not reference "
                    f"the {_FORBIDDEN_ESTATE_MARKER.upper()} estate"
                )
                raise ValueError(msg)
        return self
