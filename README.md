# viavitae-hermes-agents

Via-Vitae Hermes agents — autonomous agent services and orchestration.

## Repository governance

This repository's **settings, branch protection, CODEOWNERS and security
workflow are declared as code** in
[`viavitae-control`](https://github.com/Via-Vitae/viavitae-control). To change
org/repo policy, open a PR against `viavitae-control` — do not edit settings in
the GitHub UI.

## Requirements

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (the org-standard venv/packaging tool)

> **Ubuntu 24.04 / PEP 668:** system-wide `pip install` is blocked. Always work
> inside `.venv`.

## Quickstart

```bash
uv venv .venv               # create the project virtualenv (PEP 668-safe)
uv sync --extra dev         # install runtime + dev deps, generate uv.lock
uv run ruff check .
uv run pytest
```

## Layout

```
app/          # application package (hatchling wheel target)
  agents/     # agent definitions / orchestration
tests/        # pytest suite
```

## License

Proprietary — all rights reserved. See [LICENSE](LICENSE).
