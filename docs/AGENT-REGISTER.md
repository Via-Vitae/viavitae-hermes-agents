# Agent Register

Asset inventory of all assistive agents in the Via Vitae estate.

| Agent | Module | Responsibility | Status |
| --- | --- | --- | --- |
| Via Vitae Orchestrator | `src/viavitae_hermes/agents/orchestrator.py` | Sequences agents; enforces control gates | Scaffold |
| Intake Agent | `src/viavitae_hermes/agents/intake.py` | Normalizes requests into typed cases | Scaffold |
| Data Classification Agent | `src/viavitae_hermes/agents/classification.py` | Labels sensitivity (keyword heuristic) | Scaffold (placeholder) |
| Consent Agent | `src/viavitae_hermes/agents/consent.py` | Verifies lawful basis before processing | Scaffold |
| Information Retrieval Agent | `src/viavitae_hermes/agents/retrieval.py` | Read-only, boundary-scoped retrieval | Scaffold (NullRetrievalSource) |
| Case Summary Agent | `src/viavitae_hermes/agents/summary.py` | Bounded, source-attributed summaries | Scaffold |
| Draft Response Agent | `src/viavitae_hermes/agents/draft_response.py` | Produces drafts only; never sends | Scaffold |
| Safeguarding Escalation Agent | `src/viavitae_hermes/agents/safeguarding.py` | Raises non-suppressible alerts | Scaffold |
| Human Review Agent | `src/viavitae_hermes/agents/human_review.py` | Mandatory approval chokepoint | Scaffold |
| Audit Agent | `src/viavitae_hermes/agents/audit.py` | Records decisions to tamper-evident stream | Scaffold (in-memory) |

## Status Definitions

- **Scaffold** — implemented, tested, but not production-ready (placeholder logic, in-memory storage, unprovisioned boundary).
- **Production** — approved classifier, durable audit, provisioned boundary, security review complete.
