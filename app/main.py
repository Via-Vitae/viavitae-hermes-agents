"""Application entrypoint.

Placeholder service surface; replace with real agent orchestration wiring.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI

from app.agents.base import AgentRegistry

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="viavitae-hermes-agents", version="0.1.0")
    registry = AgentRegistry()

    @app.get("/healthz")
    def healthz() -> dict[str, object]:
        return {"status": "ok", "agents": registry.names()}

    return app


app = create_app()
