"""Smoke tests for the scaffold."""

from app.main import create_app
from fastapi.testclient import TestClient


def test_healthz() -> None:
    client = TestClient(create_app())
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
