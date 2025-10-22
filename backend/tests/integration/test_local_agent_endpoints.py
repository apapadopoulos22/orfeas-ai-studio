"""
Integration tests for lightweight LocalAgent endpoints exposed in backend/main.py

These tests run the OrfeasUnifiedServer in TESTING mode to skip heavy model
initialization, then inject a demo LocalAgent instance to validate the
status and call endpoints behave as expected.
"""

import os
import json
import sys
from pathlib import Path

import pytest


# Ensure we import from backend package
BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="module")
def flask_app():
    # Run server in testing mode to avoid heavy initializations
    os.environ["TESTING"] = "1"
    os.environ["FLASK_ENV"] = "testing"

    from main import OrfeasUnifiedServer, ProcessorMode  # type: ignore
    from local_agent_optimizer import demo_agent  # type: ignore

    server = OrfeasUnifiedServer(mode=ProcessorMode.FULL_AI)
    # Inject demo local agent so endpoints become available in test mode
    server.local_agent = demo_agent()
    app = server.app
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()


def test_local_agent_status_ok(client):
    resp = client.get("/api/local-agent/status")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get("available") is True
    assert isinstance(data.get("abilities"), list)
    # demo_agent provides 'uppercase' and 'sum' by default
    assert "uppercase" in data.get("abilities", [])


def test_local_agent_call_uppercase(client):
    payload = {"ability": "uppercase", "params": {"text": "hello"}}
    resp = client.post("/api/local-agent/call", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get("success") is True
    assert data.get("ability") == "uppercase"
    assert data.get("result") == "HELLO"


def test_local_agent_call_unknown_ability(client):
    payload = {"ability": "does_not_exist", "params": {}}
    resp = client.post("/api/local-agent/call", json=payload)
    assert resp.status_code == 404
    data = json.loads(resp.data)
    assert "Unknown ability" in data.get("error", "")
