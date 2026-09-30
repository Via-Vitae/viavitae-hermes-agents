# Retention & Erasure Schedule

**Status: Not yet defined.**

GDPR Art. 5(1)(e) requires personal data to be kept no longer than necessary. Art. 17 provides the right to erasure. This document defines retention periods and erasure procedures.

## Tension: Append-Only Audit vs. Right to Erasure

The audit stream is append-only and tamper-evident (SHA-256 hash chain). This conflicts with Art. 17 erasure requests.

### Resolution Strategy (TODO)

- **Case records** (personal data): erasure-eligible under Art. 17.
- **Audit log** (processing actions): retained under legal obligation (Art. 17(3)(b)) or legitimate interest (Art. 17(3)(e)).
- **Pseudonymization:** audit log entries referencing erased case IDs should be pseudonymized (replace case_id with hash or "erased").
- **Retention periods:** define per data category (e.g., case records: 7 years; audit log: 10 years; consent records: duration of processing + 3 years).

## Required Definitions (TODO)

| Data Category | Retention Period | Erasure Procedure | Legal Basis for Retention |
| --- | --- | --- | --- |
| Case records | TBD | TBD | TBD |
| Audit log | TBD | Pseudonymize case_id references | Legal obligation (Art. 17(3)(b)) |
| Consent records | Duration of processing + 3 years | Erase after retention period | Consent (Art. 6(1)(a)) |
| Personal data in eval datasets | N/A (synthetic only) | N/A | N/A |

## Next Steps

1. Define retention periods with legal counsel.
2. Implement erasure procedures in code (case records, consent records).
3. Implement pseudonymization for audit log.
4. Document in `config/retention/`.

**Do not handle real personal data until retention schedule is defined and implemented.**
