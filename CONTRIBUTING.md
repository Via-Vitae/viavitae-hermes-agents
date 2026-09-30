# Contributing

## Branch & review policy

- Default branch `main` is protected: no direct pushes, no force-pushes, no
  deletions, linear history required.
- All changes go through a pull request (enforced by branch protection declared
  in `viavitae-control`).
- Single-member org note: approving-review-count is currently `0`; raise to `1`
  in `viavitae-control` once a second reviewer exists.

## Workflow

VERIFY FIRST → branch → commit (Conventional Commits) → push → open PR →
review → squash-merge → VERIFY AGAIN.

## Quality gates

Run before pushing:

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy app
uv run pytest
uv run bandit -c pyproject.toml -r app
```

`pre-commit` runs gitleaks + hygiene hooks locally; CI runs gitleaks as a
compensating control.
