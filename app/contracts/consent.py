"""Consent and lawful-basis contracts (GDPR Art. 6)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class LawfulBasis(StrEnum):
    """Lawful bases for processing personal data."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"
    NONE = "none"


class ConsentState(BaseModel):
    """Result of a consent/lawful-basis check. Fails closed when unverified."""

    model_config = ConfigDict(frozen=True)

    verified: bool
    lawful_basis: LawfulBasis
    reason: str = ""
