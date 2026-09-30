"""Data Classification Agent — conservative sensitivity labelling.

Placeholder heuristic for the scaffold. Classification biases toward the more
protective label and never defaults to PUBLIC. Replace with the approved
classifier before handling real personal data.
"""

from __future__ import annotations

from app.contracts.cases import Case, SensitivityLevel

_SPECIAL_CATEGORY_TOKENS = frozenset(
    {
        "health",
        "medical",
        "diagnosis",
        "biometric",
        "genetic",
        "religion",
        "ethnic",
        "racial",
        "criminal",
        "sexual orientation",
    }
)
_PERSONAL_TOKENS = frozenset(
    {
        "name",
        "email",
        "phone",
        "address",
        "dob",
        "date of birth",
        "national insurance",
        "passport",
        "account number",
    }
)


class DataClassificationAgent:
    """Assigns a sensitivity label, failing toward the more protective level."""

    name: str = "classification-agent"

    def classify(self, case: Case) -> Case:
        text = f"{case.subject} {case.raw_input}".casefold()
        level = SensitivityLevel.INTERNAL
        if any(token in text for token in _PERSONAL_TOKENS):
            level = SensitivityLevel.PERSONAL
        if any(token in text for token in _SPECIAL_CATEGORY_TOKENS):
            level = SensitivityLevel.SPECIAL_CATEGORY
        return case.model_copy(update={"sensitivity": level})
