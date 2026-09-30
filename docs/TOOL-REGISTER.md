# Tool Register

Closed allowlist of permitted tools. **No generic MCP tool discovery** (excluded capability).

## Permitted Tools

| Tool | Purpose | Approval | Status |
| --- | --- | --- | --- |
| (none yet) | — | — | — |

## Rules

- **Deny-by-default.** Tools must be explicitly allowlisted.
- **Reconciled with `config/tools/`.** Config and this register must match.
- **No autonomous external communication.** Tools cannot initiate outbound calls without human approval.
- **Audit all invocations.** Every tool use recorded in the audit stream.

## Adding a Tool

1. Submit PR adding tool to this register and `config/tools/`.
2. Security review (threat model update, boundary analysis).
3. CODEOWNERS approval.
4. Update `evaluations/security/` with tool-specific tests.

Status: **Empty.** No tools permitted yet.
