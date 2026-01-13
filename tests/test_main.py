


import pytest
import os

TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_chronicle.db'))
os.environ["CHRONICLE_KEEPER_DB_PATH"] = TEST_DB_PATH
from db.test_db_setup import setup_test_db, teardown_test_db

@pytest.fixture(scope="module")
def client():
    setup_test_db(TEST_DB_PATH)
    # Import app only after DB is set up, so all global objects and threads see the tables
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as c:
        yield c
    teardown_test_db(TEST_DB_PATH)

def test_ping(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.json()["status"] == "chronicle-keeper alive"

def test_event_validation_rejects_missing_type(client):
    resp = client.post("/event", json={"timestamp": 123})
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"

def test_event_validation_accepts_valid(client):
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

def test_get_world_state(client):
    resp = client.get("/world/state")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)

def test_get_recent_events(client):
    resp = client.get("/world/events/recent?limit=2")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
