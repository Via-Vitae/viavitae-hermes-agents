# Via Vitae Hermes Agents — Compliance Mapping

Target frameworks: **SOC 2 Type II**, **GDPR**, **ISO/IEC 27001**.

> Status: **design intent only — NOT attested, NOT audited, NOT approved.**
> This document maps code-level controls to framework control *intent*. It does
> not assert that any control is operating effectively, and it fabricates no
> evidence. Every item under "Open items" requires human sign-off before any
> compliance claim is made.

## 1. Control mapping (design intent)

| Control intent | Framework reference | Where addressed in code | Status |
| --- | --- | --- | --- |
| Lawful basis before processing personal data | GDPR Art. 6; Art. 9 (special category) | `ConsentAgent` fails closed; orchestrator halts before retrieval | Implemented (scaffold logic) |
| Data minimization / purpose limitation | GDPR Art. 5(1)(b),(c) | Bounded summaries; read-only retrieval; no generic DB access | Partial (heuristic) |
| Integrity & confidentiality | GDPR Art. 5(1)(f); ISO 27001 A.8 | Deny-by-default egress; estate isolation; typed contracts | Implemented (scaffold) |
| Accountability / record of processing | GDPR Art. 5(2), Art. 30 | Append-only hash-chained `AuditStream` | Implemented (in-memory) |
| Human oversight of automated processing | GDPR Art. 22 | Mandatory `HumanReviewAgent` gate; no auto-approval | Implemented |
| Logical access isolation | SOC 2 CC6.1–CC6.3; ISO 27001 A.5.15 | Separate deployment identity, secrets, KMS key (declared) | Declared, not provisioned |
| Change management | SOC 2 CC8.1; ISO 27001 A.8.32 | Protected `main`, PR review, governance-as-code in `viavitae-control` | Process-level |
| Monitoring / tamper-evidence | SOC 2 CC7.1–CC7.2 | Hash-chained audit; `AuditTamperError` on rewrite | Implemented (in-memory) |
| Vulnerability management | SOC 2 CC7.1; ISO 27001 A.8.8 | ruff (bandit rules), mypy strict, bandit, gitleaks in CI | Implemented |

## 2. Data boundary (segregation) controls

`BoundarySettings` requires all seven separate controls and rejects any
cross-estate (`jol`) reference at load time (fail-closed):

1. Separate database
2. Separate vector index
3. Separate KMS key
4. Separate checkpoints namespace
5. Separate audit stream
6. Separate secrets reference
7. Separate deployment identity

These are **declared and validated in configuration**, but not yet bound to
provisioned infrastructure. Binding is an operational task tracked below.

## 3. Structural exclusions as compliance controls

The excluded capabilities (GitHub write, Bitrix, donations, marketplace, DevOps
mutation, shared JOL memory, generic DB access, generic MCP discovery,
autonomous external communication, autonomous decisions about people) reduce
attack surface and scope. `tests/test_exclusions.py` enforces their absence as a
build gate, providing repeatable evidence for scope-boundary claims.

## 4. Known tension: append-only audit vs. right to erasure

An append-only, tamper-evident audit trail can conflict with GDPR Art. 17
(erasure). This is **unresolved** and requires a documented retention and
lawful-hold policy that distinguishes:

- personal data in the *case record* (erasure-eligible), from
- the *audit log* of processing actions (retained under legal obligation,
  Art. 17(3)(b)/(e)), with pseudonymization where feasible.

No erasure procedure is implemented in this scaffold.

## 5. Open items requiring human sign-off (NOT done)

These are deliberately not fabricated. Each must be produced and approved by the
accountable owner before any compliance assertion:

- [ ] **DPIA** (GDPR Art. 35) — likely mandatory: special-category data and
      systematic processing are in scope.
- [ ] **Record of Processing Activities** (Art. 30) entry for this estate.
- [ ] **Retention & erasure schedule** resolving Section 4.
- [ ] **Lawful basis determination** per processing purpose (the scaffold only
      checks that *a* basis is present; it does not select or justify one).
- [ ] **Provisioning** of the seven separate boundary controls, with evidence of
      non-sharing (network, KMS, secrets, identity).
- [ ] **Durable audit storage** with access controls and independent monitoring.
- [ ] **Approved data classifier** to replace the keyword heuristic.
- [ ] **ADRs** for the isolation and human-supervision decisions (none exist yet;
      do not cite any).
- [ ] **SOC 2 control narratives** and **ISO 27001 SoA** entries, if pursued.
- [ ] **Penetration test / third-party review** before production.

## 6. Verification evidence available today

The only compliance-relevant evidence this repository can currently produce is
automated and repeatable via CI (`ruff check`, `ruff format --check`,
`mypy app`, `pytest`) plus `gitleaks` and `bandit`. Test names encode the
enforced invariants (consent halt, non-suppressible safeguarding, mandatory
human review, exclusion grep, audit tamper detection). This is engineering
evidence, **not** a compliance attestation.
