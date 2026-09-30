# Data Protection Impact Assessment (DPIA)

**Status: Not yet conducted.**

GDPR Art. 35 requires a DPIA when processing is likely to result in a high risk to individuals. This estate processes personal data (and potentially special-category data per Art. 9), making a DPIA **likely mandatory** before handling real data.

## Required Sections (Art. 35(7))

1. **Systematic description** of processing operations and purposes.
2. **Assessment of necessity and proportionality** (Art. 5).
3. **Assessment of risks** to data subjects (unauthorized access, loss, discrimination).
4. **Mitigations** (technical/organizational measures: encryption, access controls, audit, human oversight).
5. **Consultation** with DPO and (if required) supervisory authority.

## Current State

- **Processing:** assistive, human-supervised agent system.
- **Data types:** personal data (email, name, etc.), potentially special-category (health, biometric, etc.).
- **Mitigations in place:** consent gates, deny-by-default egress, audit trail, human-review chokepoint, estate isolation.
- **Gaps:** durable audit storage, approved classifier, provisioned Boundary (declared but not bound to real infra).

## Next Steps

1. Conduct DPIA with DPO.
2. Document risks and mitigations.
3. If residual risk is high, consult supervisory authority (Art. 36).
4. Review and update DPIA when processing changes.

**Do not handle real personal data until DPIA is complete and approved.**
