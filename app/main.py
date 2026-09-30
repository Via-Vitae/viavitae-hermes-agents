"""Application entrypoint.

Exposes a dependency-free health surface listing the assistive agent
components. The orchestrator is constructed on demand with validated boundary
settings (fail-closed); it is never instantiated at import time, so the service
can report health without any secret or data-boundary configuration present.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI

from app.agents import AGENT_COMPONENTS

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="viavitae-hermes-agents", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict[str, object]:
        return {"status": "ok", "agents": list(AGENT_COMPONENTS)}

    return app


app = create_app()
