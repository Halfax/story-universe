import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_ping():
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.json()["status"] == "chronicle-keeper alive"

def test_event_validation_rejects_missing_type():
    resp = client.post("/event", json={"timestamp": 123})
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"

def test_event_validation_accepts_valid():
    event = {
        "type": "character_action",
        "timestamp": 9999999999,
        "character_id": "1",
        "location_id": "100",
        "description": "Test event"
    }
    resp = client.post("/event", json=event)
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"

def test_get_world_state():
    resp = client.get("/world/state")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)

def test_get_recent_events():
    resp = client.get("/world/events/recent?limit=2")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
