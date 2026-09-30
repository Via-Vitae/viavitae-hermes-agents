#!/usr/bin/env bash
# One-shot local dev bootstrap (PEP 668-safe: everything lands in .venv).
set -euo pipefail
cd "$(dirname "$0")/.."
uv venv .venv
uv sync --extra dev
uv run pre-commit install
echo "Bootstrap complete. Activate with: source .venv/bin/activate"
