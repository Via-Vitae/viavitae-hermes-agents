# Approval Matrix

Defines which actions require human approval and which reviewer roles are authorized.

## Actions Requiring Approval

| Action | Required Approval | Reviewer Role | Can Escalate? |
| --- | --- | --- | --- |
| Case approval (non-escalated) | Human Review Agent | human-reviewer | No |
| Case approval (escalated) | Human Review Agent + Safeguarding | human-reviewer + safeguarding-officer | Yes |
| Tool invocation (if added) | TBD | TBD | TBD |
| Policy change (config/) | PR review + CODEOWNERS | architect | Yes |

## Reviewer Roles

- **human-reviewer** — authorized to approve/reject cases at the mandatory human-review gate.
- **safeguarding-officer** — authorized to handle safeguarding escalations; cannot be bypassed.
- **architect** — authorized to approve policy/config changes.

## Rules

- **No auto-approval.** Every action in the "Required Approval" column requires explicit human decision.
- **Attributable.** Every approval records reviewer identity and rationale (audit trail).
- **Non-suppressible.** Safeguarding escalations cannot be overridden by lower-privilege reviewers.

Status: **Initial scaffold.** Reviewer roles are conceptual; actual identity/authN not yet provisioned.
