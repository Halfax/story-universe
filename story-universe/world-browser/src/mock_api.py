"""Lightweight mock API server for World Browser local development.

Run with:
    pip install fastapi uvicorn
    uvicorn world_browser.src.mock_api:app --reload --port 8002

Set `MOCK_MODE=1` in the UI to point at this server instead of the Pi backend.
"""
import os
import time
import uuid
from typing import Any, Dict

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="World Browser Mock API")

# Simple in-memory world state for mock purposes
world_state: Dict[str, Any] = {
    "characters": {
        "1": {"id": 1, "name": "Alice", "status": "alive", "location_id": 100},
        "2": {"id": 2, "name": "Borin", "status": "alive", "location_id": 101},
    },
    "locations": {
        "100": {"id": 100, "name": "Town", "description": "A small town."},
        "101": {"id": 101, "name": "Forest", "description": "Dark woods."},
    },
    "factions": {
        "10": {"id": 10, "name": "Militia", "ideology": "defense"}
    },
    "recent_events": []
}


class EventPayload(BaseModel):
    id: str | None = None
    type: str
    timestamp: int | None = None
    description: str | None = None
    involved_characters: list | None = None
    involved_locations: list | None = None
    metadata: dict | None = None


def _make_id() -> str:
    return f"mock_evt_{int(time.time())}_{uuid.uuid4().hex[:8]}"


@app.get("/world")
def get_world():
    return world_state


@app.get("/events")
def list_events():
    return list(world_state.get("recent_events", []))


@app.post("/event")
def post_event(payload: EventPayload, x_api_key: str | None = Header(None)):
    # Optional simple API key check if CHRONICLE_API_KEY set
    configured = os.environ.get("CHRONICLE_API_KEY")
    if configured and x_api_key != configured:
        raise HTTPException(status_code=401, detail="Invalid API key")

    ev = payload.dict()
    if not ev.get("id"):
        ev["id"] = _make_id()
    if not ev.get("timestamp"):
        ev["timestamp"] = int(time.time())

    # Minimal validation: require type
    if not ev.get("type"):
        return {"status": "rejected", "reason": "missing type"}

    # Append to recent_events (bounded)
    recent = world_state.setdefault("recent_events", [])
    recent.insert(0, {"id": ev["id"], "timestamp": ev["timestamp"], "type": ev["type"], "description": ev.get("description")})
    # Keep last 200
    world_state["recent_events"] = recent[:200]

    return {"status": "accepted", "id": ev["id"]}


@app.get("/health")
def health():
    return {"status": "ok"}
