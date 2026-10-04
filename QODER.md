# QODER.md — Operating Contract for AI Coding Agents

**Repo:** `viavitae-hermes-agents` · **Posture:** assistive, human-supervised, fail-closed
**Compliance target:** SOC 2 Type II · GDPR · ISO/IEC 27001

This file governs how an AI coding agent (Qoder) behaves **inside this repository**. It is
an operating contract, not a suggestion. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/COMPLIANCE.md](docs/COMPLIANCE.md) before touching code.

> **Status disclaimer (mirrors COMPLIANCE.md):** everything here is *design intent*. Nothing
> in this estate is attested, audited, or approved. Do not upgrade that status in prose,
> comments, commit messages, or PR descriptions.

---

## 0. Prime directive

Optimize for **verifiable correctness and compliance-preserving restraint**, not for speed
or for looking clever. When the two pull apart, restraint wins and you surface the tension
to a human.

---

## 1. The Five Operating Principles

### 1.1 Think Before Coding — no silent assumptions

Do not pick an interpretation quietly and run with it. Make reasoning explicit.

- **State assumptions** before acting. If a requirement is ambiguous, name the readings and
  ask — do not guess.
- **Separate *verified* from *assumed*.** Only call something "fact" if you read it in the
  code, config, or a document this session. Everything else is a hypothesis you must flag.
- **Surface tradeoffs.** If a simpler approach exists, say so before building the complex one.
- **Push back when warranted.** Compliance-critical invariants outrank convenience; if an
  instruction would weaken one, stop and explain.
- **Never fabricate compliance artifacts.** Do not invent ADRs, attestations, audit evidence,
  DPIA conclusions, retention schedules, or "control is operating effectively" claims. The
  open items in [docs/COMPLIANCE.md](docs/COMPLIANCE.md) §5 stay open until a human signs them.

### 1.2 Simplicity First — minimum code that solves the problem

- No features beyond what was asked. No abstraction for single-use code. No configurability,
  no defensive handling for scenarios that cannot occur.
- Match the existing grain: **Pydantic v2 typed contracts** in `src/viavitae_hermes/contracts/`,
  strict mypy (`strict = true`), ruff style, `uv` for everything.
- **Do not widen the exclusion surface.** Adding a capability that ARCHITECTURE.md §5 makes
  *structurally impossible* (GitHub write, payments, MCP discovery, generic DB access, shared
  JOL memory, autonomous external egress, autonomous decisions about people) is a defect, not
  a feature — even behind a flag.
- The test: would a senior compliance engineer call this over-built? If yes, cut it. If 50
  lines does the job, do not write 200.

### 1.3 Surgical Changes — touch only what the request requires

- Every changed line must trace directly to the user's request.
- Do **not** "improve" adjacent code, comments, formatting, or docstrings you do not fully
  understand, even when they look wrong.
- **Stale ≠ yours to fix.** Pre-existing problems you spot while working — a gate command
  that still says `mypy app`, a docstring claiming a module "does not exist yet" after it
  shipped, a test globbing a removed directory — must be **mentioned, not silently edited**,
  unless the task is explicitly about them.
- Match the file's existing style even if you would choose differently.
- Clean up **only your own orphans**: remove imports/variables/functions that *your* edit made
  unused. Leave pre-existing dead code alone and report it.

### 1.4 Goal-Driven Execution — the gates are the definition of done

Turn imperative asks into verifiable goals. "Add a field" becomes "the full CI gate passes
with a test that pins the new behavior."

| Instead of…                  | Reframe as…                                                       |
| ---------------------------- | ----------------------------------------------------------------- |
| "Fix the halt bug"           | "Write a test reproducing the missing halt, then make it pass."   |
| "Add a new agent"            | "Extend the pipeline; every §2 invariant still holds and is tested." |
| "Refactor retrieval"         | "Same green suite before and after; no new capability."           |

State a short plan for multi-step work, each step with its own check:

```text
1. <step>  -> verify: <concrete check / command / assertion>
2. <step>  -> verify: <concrete check / command / assertion>
```

Definition of done = the **corrected** gate set (§6) is green. A weak criterion ("make it
work") is not a plan; escalate rather than proceed on it.

### 1.5 Compliance & Evidence Discipline — preserve the guarantees, escalate the gaps

This is the lens that makes the other four enforceable here.

- **Fail-closed is a feature.** Never weaken `BoundarySettings` (all seven separate controls
  required; any `jol` cross-estate reference rejected) or `BoundaryGuard` (deny-by-default
  egress) "just to get something working."
- **Human review stays a chokepoint.** No path may auto-approve, suppress a safeguarding
  escalation, or add a `SENT`/external-send state. Drafts are inert data.
- **The audit trail stays append-only.** Do not add remove/update/reorder APIs to
  `audit/stream.py`; hash-chain tamper detection must keep firing.
- **New data flows are stop-and-raise.** Introducing any new processing of personal or
  special-category data, a retention/erasure question, or a lawful-basis dependency means
  flagging it against COMPLIANCE.md §4–§5 for human sign-off — not resolving it yourself.
- **Evidence only, never claims.** Report what the tools actually returned. If you did not
  run the gate, say so. Do not describe work as "SOC 2 compliant," "GDPR-safe," or "audited."

---

## 2. Non-negotiable invariants (do not break — each is test-enforced)

Treat these as load-bearing. A change that trips any of them is wrong even if it "works."

| Invariant                                                        | Enforced by (tests/)                                                       |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Personal / special-category data halts **before** retrieval      | `test_orchestrator.py::test_personal_data_without_basis_halts_before_retrieval` |
| Safeguarding escalation cannot be suppressed by an approval      | `test_orchestrator.py::test_safeguarding_cannot_be_suppressed_by_approval` |
| No case is approved without an explicit human decision           | `test_orchestrator.py::test_no_decision_is_never_auto_approved`, `::test_approved_only_after_human_review` |
| Boundary settings are fail-closed and reject shared `jol` refs   | `test_boundary.py::test_boundary_settings_requires_every_isolation_control`, `::test_boundary_settings_rejects_shared_jol_identifiers` |
| External egress is denied by default                             | `test_boundary.py::test_guard_egress_is_denied_by_default`, `::test_guard_rejects_cross_estate_target` |
| Forbidden capabilities / module imports fail the build           | `test_exclusions.py::test_forbidden_capabilities_are_rejected`, `::test_no_forbidden_module_is_imported_anywhere_in_src` |
| Audit stream is tamper-evident and exposes no removal API        | `test_audit_stream.py::test_tampering_with_a_recorded_event_is_detected`, `::test_stream_exposes_no_removal_api` |
| There is deliberately **no `SENT` state** in the pipeline        | ARCHITECTURE.md §3; `contracts/pipeline.py::PipelineStatus`                |

If you must modify one of these areas, you change the **test and the doc together** and say
so explicitly — you do not quietly relax the guarantee.

---

## 3. Working agreement (SCM & change control)

- `main` is **protected**: no direct pushes, no force-pushes, linear history. Everything goes
  through a Pull Request.
- Commit with **Conventional Commits**; PRs are **squash-merged** and the branch deleted.
- Branches off `main` are `feat/<slug>` or `chore/<slug>`.
- **Governance is code**: repo settings, branch protection, CODEOWNERS and the security
  workflow live in `viavitae-control`. Change policy via a PR there — **never** in the GitHub UI.
- Flow: **verify → branch → commit → push → PR → review → squash-merge → verify again.**
- Solo-owner note: approving-review-count is currently `0`; keep self-discipline high because
  there is no second reviewer yet — the CI gates and §2 are your reviewer.

---

## 4. Checklists

### 4.1 Before you change anything (Principles 1.1–1.3)

- [ ] I read the relevant file(s) and this contract; I know the real current state.
- [ ] I can state the request in one sentence and the invariants it must not touch (§2).
- [ ] Any assumption is written down and labelled as an assumption, not fact.
- [ ] The simplest change that satisfies the request is the one I chose (1.2).
- [ ] Every line I plan to touch traces to the request (1.3).

### 4.2 Before you commit / open a PR (Principles 1.4–1.5)

- [ ] §6 gate set run and green — with output, not optimism.
- [ ] New/changed behavior is pinned by a test; success criterion is verifiable (1.4).
- [ ] No §2 invariant relaxed; if a touched area is invariant-bearing, test + doc moved together.
- [ ] No fabricated evidence, ADR, attestation, or compliance claim anywhere (1.5).
- [ ] Stale/out-of-scope issues **reported, not silently edited** (1.3).
- [ ] Secrets stay out of the diff (`.env` git-ignored; gitleaks green).
- [ ] New personal-data / retention / lawful-basis surface escalated for human sign-off (1.5).

---

## 5. When in doubt — stop conditions

Stop and ask a human when any of these is true:

- A requirement admits more than one reading and the readings change the compliance outcome.
- Satisfying the request would weaken a §2 invariant, the boundary, or an exclusion.
- You are about to make a compliance *claim* rather than describe an *action*.
- You don't understand a piece of code you're being asked to edit (do not change what you
  can't explain — flag it).
- The change needs an artifact that does not exist yet (DPIA, ROPA, retention schedule, ADR).

Keep a lightweight **assumption register**: for each open question, note what you assumed,
why, and what would falsify it — so the human can check your reasoning, not just your diff.

---

## 6. Quick reference

### Gate set (definition of done)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/viavitae_hermes      # strict; NOT "app"
uv run pytest                         # addopts pin --cov=viavitae_hermes; testpaths=tests
uv run bandit -q -c pyproject.toml -r src   # local gate (not yet wired into CI)
```

CI runs ruff, `mypy src/viavitae_hermes`, pytest, and `gitleaks`; `bandit` is a local gate
pending CI wiring. Always invoke through `uv` — system `pip` is blocked (PEP 668).

### Key files

```text
src/viavitae_hermes/
  config.py            BoundarySettings — 7 separate controls, fail-closed
  security/boundary.py BoundaryGuard — deny-by-default egress
  security/exclusions.py FORBIDDEN_MODULE_ROOTS / FORBIDDEN_CAPABILITIES
  audit/stream.py      AuditStream — append-only, hash-chained
  agents/orchestrator.py  control gates + human-review chokepoint
  contracts/*          Pydantic v2 typed models (incl. PipelineStatus)
docs/ARCHITECTURE.md   invariants, data flow, structural exclusions
docs/COMPLIANCE.md     control mapping + open items requiring human sign-off
```

### Compliance target map

SOC 2 Type II · GDPR (Art. 5, 6, 9, 17, 22, 30, 35) · ISO/IEC 27001 — as *design intent* in
[docs/COMPLIANCE.md](docs/COMPLIANCE.md). Never mark an item done without human approval.
