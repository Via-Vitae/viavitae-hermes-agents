"""Structural enforcement of the Via Vitae capability exclusions.

The initial estate must make excluded capabilities impossible, not merely
unused. Two layers cooperate:

* :data:`FORBIDDEN_CAPABILITIES` — a runtime deny-list checked before any
  capability is exercised.
* :data:`FORBIDDEN_MODULE_ROOTS` — third-party import roots whose presence would
  imply an excluded capability. A structural test asserts none are imported
  anywhere under ``app``.
"""

from __future__ import annotations


class ForbiddenCapabilityError(RuntimeError):
    """Raised when an excluded capability is requested."""


FORBIDDEN_CAPABILITIES: frozenset[str] = frozenset(
    {
        "devops_mutation",
        "github_write",
        "donation_workflow",
        "marketplace_workflow",
        "bitrix_access",
        "shared_jol_memory",
        "autonomous_external_communication",
        "autonomous_decision_about_person",
        "generic_database_access",
        "generic_mcp_discovery",
    }
)

FORBIDDEN_MODULE_ROOTS: frozenset[str] = frozenset(
    {
        "github",
        "PyGithub",
        "bitrix",
        "bitrix24",
        "mcp",
        "sqlalchemy",
        "psycopg",
        "pymongo",
        "redis",
        "boto3",
        "botocore",
        "requests",
        "stripe",
        "braintree",
    }
)


def assert_capability_permitted(capability: str) -> None:
    """Raise if the capability is excluded from the Via Vitae estate."""
    if capability in FORBIDDEN_CAPABILITIES:
        msg = f"capability {capability!r} is excluded from the Via Vitae estate"
        raise ForbiddenCapabilityError(msg)
