
# FastAPI app entry for Chronicle Keeper (Raspberry Pi 5)
from fastapi import FastAPI, Request

from src.services.continuity import ContinuityValidator
from src.db.database import get_connection

from src.messaging.publisher import TickPublisher
from src.services.clock import start_world_clock


app = FastAPI()



# Start the world clock and tick broadcasting thread using FastAPI startup event
@app.on_event("startup")
def start_world_clock_on_startup():
    print("[ChronicleKeeper] FastAPI startup event: starting world clock thread...")
    from src.services.clock import start_world_clock
    start_world_clock()

# Fallback: If running as a script (not under Uvicorn), start the world clock directly
if __name__ == "__main__":
    print("[ChronicleKeeper] __main__ entry: starting world clock thread...")
    from src.services.clock import start_world_clock
    start_world_clock()

# Dummy world state for demonstration (replace with real DB/state)
world_state = {
    "characters": {"1": {"name": "Alice"}},
    "locations": {"100": {"name": "Town"}}
}
validator = ContinuityValidator(world_state)

@app.get("/ping")
def ping():
    return {"status": "chronicle-keeper alive"}



publisher = TickPublisher(address="tcp://127.0.0.1:5555", bind=False)  # Connect, do not bind

@app.post("/event")
async def ingest_event(event: dict):
    is_valid, reason = validator.validate_event(event)
    if not is_valid:
        return {"status": "rejected", "reason": reason}
    # Store event in DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO events (timestamp, type, description, involved_characters, involved_locations, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event.get("timestamp"),
        event.get("type"),
        event.get("description"),
        str(event.get("involved_characters", [])),
        str(event.get("involved_locations", [])),
        str(event.get("metadata", {}))
    ))
    conn.commit()
    conn.close()
    # Broadcast event to other nodes
    publisher.publish_event(event)
    return {"status": "accepted"}


from src.db.database import get_connection

@app.get("/world/state")
def get_world_state():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT key, value FROM world_state")
    state = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return state

@app.get("/world/characters")
def get_characters():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM characters")
    chars = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
    conn.close()
    return chars

@app.get("/world/locations")
def get_locations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM locations")
    locs = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
    conn.close()
    return locs


@app.get("/world/events/recent")
def get_recent_events(
    limit: int = 50,
    offset: int = 0,
    event_type: str = None,
    character_id: int = None,
    location_id: int = None
):
    """
    Get recent events with optional filtering and pagination.
    - limit: max number of events
    - offset: skip this many events
    - event_type: filter by event type
    - character_id: filter by involved character
    - location_id: filter by involved location
    """
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM events"
    filters = []
    params = []
    if event_type:
        filters.append("type = ?")
        params.append(event_type)
    if character_id is not None:
        filters.append("involved_characters LIKE ?")
        params.append(f'%{character_id}%')
    if location_id is not None:
        filters.append("involved_locations LIKE ?")
        params.append(f'%{location_id}%')
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    c.execute(query, params)
    events = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
    conn.close()
    return events
