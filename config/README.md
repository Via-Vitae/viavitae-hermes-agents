# Configuration (policy-as-code)

Non-secret, change-controlled policy that governs agent behavior. All changes require PR review and are tracked in git history.

## Structure

- `agents/` — agent-specific configuration (timeouts, retry policies, feature flags)
- `tools/` — closed allowlist of permitted tools (reconciled with `docs/TOOL-REGISTER.md`)
- `models/` — model selection, versioning, fallback chains
- `retention/` — data retention and erasure schedules (GDPR Art. 5(1)(e), Art. 17)
- `approvals/` — approval matrix as data (reconciled with `docs/APPROVAL-MATRIX.md`)

## Rules

- **No secrets.** Reference KMS or secret-manager paths only.
- **Change-controlled.** All edits via PR; CODEOWNERS enforces review.
- **Integrity-protected.** Loaded from versioned, trusted source at runtime.
