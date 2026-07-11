"""API key auth on /render and generate routes."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from tests.conftest import FIXTURES_DIR

TEST_API_KEY = "test-api-key-b22"


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    get_settings.cache_clear()
    monkeypatch.setenv("API_KEY", TEST_API_KEY)
    get_settings()
    return TestClient(app)


def _minimal_coa_render_body() -> dict:
    fixture = json.loads((FIXTURES_DIR / "glycine_coa_gcn010226.json").read_text(encoding="utf-8"))
    return {"document_type": "coa", "payload": fixture}


def test_render_missing_api_key_returns_401(api_client: TestClient):
    response = api_client.post("/render", json=_minimal_coa_render_body())
    assert response.status_code == 401
    assert "API key" in response.json()["detail"]


def test_render_wrong_api_key_returns_401(api_client: TestClient):
    response = api_client.post(
        "/render",
        json=_minimal_coa_render_body(),
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401
    assert "API key" in response.json()["detail"]


def test_render_valid_api_key_not_401(api_client: TestClient):
    response = api_client.post(
        "/render",
        json=_minimal_coa_render_body(),
        headers={"X-API-Key": TEST_API_KEY},
    )
    assert response.status_code != 401
