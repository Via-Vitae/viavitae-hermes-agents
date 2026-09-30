"""Consent Agent — verify a lawful basis before personal data is processed.

Fails closed: unclassified data, or personal data without a lawful basis, is
never marked verified.
"""

from __future__ import annotations

from viavitae_hermes.contracts.cases import Case
from viavitae_hermes.contracts.consent import ConsentState, LawfulBasis


class ConsentAgent:
    """Determines whether processing may lawfully proceed."""

    name: str = "consent-agent"

    def evaluate(self, case: Case) -> ConsentState:
        if case.sensitivity is None:
            return ConsentState(
                verified=False,
                lawful_basis=LawfulBasis.NONE,
                reason="unclassified data cannot be processed",
            )
        if not case.sensitivity.requires_lawful_basis:
            return ConsentState(
                verified=True,
                lawful_basis=case.lawful_basis,
                reason="no lawful basis required for non-personal data",
            )
        if case.lawful_basis is LawfulBasis.NONE:
            return ConsentState(
                verified=False,
                lawful_basis=LawfulBasis.NONE,
                reason="personal data without a lawful basis",
            )
        return ConsentState(
            verified=True,
            lawful_basis=case.lawful_basis,
            reason="lawful basis present",
        )
