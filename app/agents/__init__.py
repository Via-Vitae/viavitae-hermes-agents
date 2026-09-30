"""Agent definitions and orchestration for the Via Vitae estate.

The orchestrator factory lives in :mod:`app.agents.orchestrator` and is imported
on demand (never at package import) so that the health surface stays free of any
boundary configuration dependency.
"""

from __future__ import annotations

# Human-readable inventory of the assistive, human-supervised components.
AGENT_COMPONENTS: tuple[str, ...] = (
    "Via Vitae Orchestrator",
    "Intake Agent",
    "Data Classification Agent",
    "Consent Agent",
    "Information Retrieval Agent",
    "Case Summary Agent",
    "Draft Response Agent",
    "Safeguarding Escalation Agent",
    "Human Review Agent",
    "Audit Agent",
)
