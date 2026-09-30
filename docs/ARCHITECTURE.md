# Via Vitae Hermes Agents — Architecture

Status: initial scaffold. Operating posture is strictly **assistive and
human-supervised**. Nothing in this estate acts autonomously on, or communicates
externally about, people.

## 1. Purpose and isolation goal

`viavitae-hermes-agents` is intended to be the **most isolated** repository and
deployment in the Via-Vitae estate. It shares no database, vector index, KMS key,
checkpoint store, audit stream, secrets, or deployment identity with any other
estate (notably not with the JOL operational estate). Isolation is enforced in
code, not by convention.

## 2. Component inventory

| Component | Module | Responsibility |
| --- | --- | --- |
| Via Vitae Orchestrator | `app/agents/orchestrator.py` | Sequences agents; enforces control gates; holds no data-store or network access |
| Intake Agent | `app/agents/intake.py` | Normalizes an `IntakeRequest` into an immutable `Case` (no I/O) |
| Data Classification Agent | `app/agents/classification.py` | Labels sensitivity; fails toward the more protective level |
| Consent Agent | `app/agents/consent.py` | Verifies a lawful basis before personal data is processed; fails closed |
| Information Retrieval Agent | `app/agents/retrieval.py` | Read-only, boundary-scoped retrieval via an injected source |
| Case Summary Agent | `app/agents/summary.py` | Bounded, source-attributed summary for human review |
| Draft Response Agent | `app/agents/draft_response.py` | Produces a draft only; structurally incapable of sending |
| Safeguarding Escalation Agent | `app/agents/safeguarding.py` | Raises a protected, non-suppressible alert on risk triggers |
| Human Review Agent | `app/agents/human_review.py` | Mandatory approval chokepoint; never auto-approves |
| Audit Agent | `app/agents/audit.py` | Records every decision and data access to an append-only stream |

Supporting modules: `app/config.py` (boundary settings), `app/security/boundary.py`
(deny-by-default guard), `app/security/exclusions.py` (capability deny-list),
`app/audit/stream.py` (hash-chained audit trail), `app/contracts/*` (typed models).

## 3. Data flow and control gates

```text
IntakeRequest
   |
   v
[Intake] --> Case
   |
   v
[Classification] --> Case(sensitivity)
   |
   v
[Consent] --(unverified)--> HALTED_NO_CONSENT  (retrieval never runs)
   | (verified)
   v
[Retrieval]  read-only, in-boundary
   |
   v
[Summary]    bounded + source-attributed
   |
   v
[Safeguarding] --(escalated)--> ESCALATED (cannot be suppressed)
   |
   v
[Draft]      DRAFT only; never sent
   |
   v
[Human Review] --(no decision)--> PENDING_HUMAN_REVIEW (never auto-approved)
   | (explicit attributable decision)
   v
APPROVED | REJECTED | NEEDS_INFO
```

Every transition is written to the audit stream by the Audit Agent. The
orchestrator emits a `PipelineResult`; there is deliberately **no `SENT` state**.

Invariants enforced by the orchestrator (see `tests/test_orchestrator.py`):

- Personal/special-category data is never retrieved or summarized without a
  verified lawful basis (halt precedes retrieval).
- A safeguarding escalation overrides an approval: the case ends `ESCALATED`.
- No case is `APPROVED` without an explicit, attributable human decision.

## 4. Trust and data boundary

`BoundarySettings` (`app/config.py`) declares seven separate, non-shared controls:
separate database, vector index, KMS key, checkpoints namespace, audit stream,
secrets reference, and deployment identity. It is **fail-closed**: missing values
or any value referencing another estate (the `jol` marker) raise `ValidationError`
at load time rather than degrading to a shared default.

`BoundaryGuard` (`app/security/boundary.py`) enforces **deny-by-default egress**:
`assert_no_external_egress(...)` always raises `BoundaryViolationError` in this
release (empty allowlist), so autonomous external communication is structurally
impossible rather than merely disabled.

## 5. Structural exclusions

The following are excluded from the initial estate. They are made *impossible*,
not just unused:

| Excluded capability | Enforcement |
| --- | --- |
| DevOps mutation | No IaC/CI mutation code or credentials in-repo |
| GitHub write access | No GitHub client dependency or token; `FORBIDDEN_MODULE_ROOTS` blocks `github`/`PyGithub` |
| Donation workflows | No payment dependency (`stripe`/`braintree` blocked); no such module |
| Marketplace workflows | No such module or client |
| Bitrix access | No Bitrix client (`bitrix`/`bitrix24` blocked) |
| Shared JOL memory | Boundary settings reject any `jol` reference; retrieval is in-boundary only |
| Autonomous external communication | Deny-by-default egress guard; drafts are inert data |
| Autonomous decisions about people | Mandatory human-review gate; no auto-approval path |
| Generic database access | Retrieval only via injected read-only `RetrievalSource`; DB drivers blocked (`sqlalchemy`/`psycopg`/`pymongo`) |
| Generic MCP tool discovery | No MCP client (`mcp` blocked); no dynamic tool registry |

`tests/test_exclusions.py` fails the build if any forbidden module root is
imported anywhere under `app/`, and asserts the runtime capability deny-list.

## 6. Audit trail

`AuditStream` (`app/audit/stream.py`) is append-only and hash-chained (SHA-256).
It exposes no removal or in-place mutation API. Rewriting a recorded event breaks
the chain; the next `append`/`verify_chain` detects it and raises
`AuditTamperError`.

## 7. Scaffold limitations (honest status)

The following are intentional placeholders and must be replaced before handling
real personal data:

- **Classification** is a keyword heuristic, not an approved classifier.
- **Retrieval** uses `NullRetrievalSource` (returns nothing); no real data store
  is connected.
- **Boundary settings** declare the seven controls but are not yet wired to
  provisioned infrastructure (database, vector index, KMS, secrets manager).
- **Audit stream** is in-memory; durable, access-controlled persistence with a
  separate audit stream is a TODO (see `COMPLIANCE.md`).

## 8. Tech stack

Python 3.12, FastAPI, Pydantic v2 + pydantic-settings, structlog; `uv`-managed;
ruff + mypy(strict) + bandit + pytest. Health surface: `GET /healthz`
(dependency-free; lists components without loading boundary configuration).
