# Evaluations (agent-behavior testing)

Probabilistic and behavioral evaluations for agent systems. Distinct from `tests/` (deterministic unit/integration tests).

## Structure

- `functional/` — task completion, tool usage, multi-step reasoning
- `security/` — jailbreak resistance, prompt-leak detection, boundary enforcement
- `privacy/` — PII handling, data minimization, consent adherence
- `prompt-injection/` — direct/indirect injection resistance, instruction hierarchy
- `regression/` — behavioral regression suite (synthetic fixtures only)

## Rules

- **Synthetic data only.** No real personal data in eval datasets (GDPR minimization).
- **Reproducible.** Fixed seeds, versioned datasets, deterministic where possible.
- **Gated.** Eval results inform release decisions; failures block deployment.
