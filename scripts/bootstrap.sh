#!/usr/bin/env bash
# One-shot local dev bootstrap (PEP 668-safe: everything lands in .venv).
set -euo pipefail
cd "$(dirname "$0")/.."
uv venv .venv
uv sync --extra dev
uv run pre-commit install

# Local git wiring: squash-merged PR branches are deleted upstream, so prune the
# stale remote-tracking refs and point origin/HEAD at the real default branch.
if git remote get-url origin >/dev/null 2>&1; then
  git config fetch.prune true
  git remote set-head origin --auto
fi

echo "Bootstrap complete. Activate with: source .venv/bin/activate"
