"""Case and intake contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from viavitae_hermes.contracts.consent import LawfulBasis


class SensitivityLevel(StrEnum):
    """Data sensitivity labels, from least to most protective."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PERSONAL = "personal"
    SPECIAL_CATEGORY = "special_category"

    @property
    def requires_lawful_basis(self) -> bool:
        return self in {SensitivityLevel.PERSONAL, SensitivityLevel.SPECIAL_CATEGORY}


class IntakeRequest(BaseModel):
    """An inbound request, normalized by the Intake Agent into a Case."""

    model_config = ConfigDict(frozen=True)

    subject: str
    raw_input: str
    case_id: str | None = None
    channel: str = "internal"
    lawful_basis: LawfulBasis = LawfulBasis.NONE


class Case(BaseModel):
    """An immutable case enriched as it flows through the pipeline."""

    model_config = ConfigDict(frozen=True)

    case_id: str = Field(default_factory=lambda: uuid4().hex)
    subject: str
    raw_input: str
    channel: str = "internal"
    lawful_basis: LawfulBasis = LawfulBasis.NONE
    sensitivity: SensitivityLevel | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
