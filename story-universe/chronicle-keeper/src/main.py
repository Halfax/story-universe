
# FastAPI app entry for Chronicle Keeper (Raspberry Pi 5)
from fastapi import FastAPI, Request, HTTPException, status, Depends
from typing import Optional
import os

from src.services.continuity import ContinuityValidator
from src.db.database import get_connection
from src.db.queries import get_world_state as assemble_world_state
from src.services.inventory import list_inventory, pickup_item, use_inventory_item, equip_inventory_item
from src.services.event_consumer import handle_event as handle_event_consumer
import time

from src.messaging.publisher import TickPublisher
from src.config import ZMQ_PUB_CLIENT_ADDR
from src.services.clock import start_world_clock
from src.models.canonical_event import CanonicalEvent
from pydantic import ValidationError
import random

# Simple API key auth and rate limiting (in-memory)
API_KEY = os.environ.get("CHRONICLE_API_KEY")
ADMIN_KEY = os.environ.get("CHRONICLE_ADMIN_KEY", API_KEY)

_rate_store = {}
def rate_limit(key: str, limit: int = 60, window: int = 60):
    import time
    now = int(time.time())
    entry = _rate_store.get(key, {"ts": now, "count": 0})
    if now - entry["ts"] >= window:
        entry = {"ts": now, "count": 0}
    entry["count"] += 1
    _rate_store[key] = entry
    return entry["count"] <= limit

def require_api_key(x_api_key: Optional[str] = None):
    from fastapi import Header
    # If no API key configured, allow anonymous access
    if not API_KEY:
        def _noop():
            return None
        return Depends(_noop)

    def _inner(x_api_key: Optional[str] = Header(None)):
        key = x_api_key or ""
        if not key or (API_KEY and key != API_KEY and key != ADMIN_KEY):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        if not rate_limit(key):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        return key

    return Depends(_inner)


app = FastAPI()




# Start the world clock and tick broadcasting thread using FastAPI startup event
@app.on_event("startup")
def startup_tasks():
    print("[ChronicleKeeper] FastAPI startup event: checking environment and ensuring test DB tables...")
    # If running tests against a test DB, avoid starting the world clock thread to prevent file locks
    db_path = os.environ.get("CHRONICLE_KEEPER_DB_PATH", "")
    is_test_db = db_path.endswith("test_chronicle.db")
    if not is_test_db and not os.environ.get("CHRONICLE_DISABLE_CLOCK"):
        from src.services.clock import start_world_clock
        start_world_clock()

    # Ensure test DB tables exist if running in test mode
    try:
        from src.db.test_db_setup import setup_test_db
        if db_path:
            setup_test_db(db_path)
    except ImportError:
        pass

# Fallback: If running as a script (not under Uvicorn), start the world clock directly
if __name__ == "__main__":
    print("[ChronicleKeeper] __main__ entry: starting world clock thread...")
    from src.services.clock import start_world_clock
    start_world_clock()

# Validator now reads canonical state from DB directly
validator = ContinuityValidator(db_conn_getter=get_connection)

@app.get("/ping")
def ping():
    return {"status": "chronicle-keeper alive"}



publisher = TickPublisher(address=ZMQ_PUB_CLIENT_ADDR, bind=False)  # Connect, do not bind (address from config)

@app.post("/event")
async def ingest_event(event: dict, api_key: str = require_api_key()):
    # Accept raw dict for backward compatibility; ensure minimal fields and coerce to CanonicalEvent.
    # Auto-generate an `id` if missing to preserve previous behavior where clients didn't provide one.
    if 'id' not in event or not event.get('id'):
        event['id'] = f"evt_{int(time.time())}_{random.randint(0,9999)}"

    try:
        parsed = CanonicalEvent.model_validate(event) if hasattr(CanonicalEvent, 'model_validate') else CanonicalEvent(**event)
        evd = parsed.dict() if hasattr(parsed, 'dict') else parsed.model_dump()
    except ValidationError as ve:
        # Return 200 with rejected payload to preserve legacy behavior
        return {"status": "rejected", "reason": f"schema validation failed: {ve}"}
    except Exception:
        # Fallback: treat as rejected but include minimal reason
        return {"status": "rejected", "reason": "schema validation failed"}
    is_valid, reason = validator.validate_event(evd)
    if not is_valid:
        # Maintain backwards-compatible behavior for clients/tests: return 200 with rejected payload
        return {"status": "rejected", "reason": reason}

    # Store event in DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO events (timestamp, type, description, involved_characters, involved_locations, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        evd.get("timestamp"),
        evd.get("type"),
        evd.get("description") or str(evd.get("data", {})),
        str(evd.get("involved_characters", []) or []),
        str(evd.get("involved_locations", []) or []),
        str(evd.get("metadata", {}))
    ))
    conn.commit()
    conn.close()

    # Broadcast event to other nodes using canonical model dict
    try:
        publisher.publish_event(evd)
    except Exception:
        # Non-fatal: log and continue
        print("[ChronicleKeeper] Warning: failed to publish event")

    return {"status": "accepted", "id": evd.get("id")}

# ------------------------
# CRUD endpoints (characters, locations, factions)
# ------------------------
def require_admin(api_key: str = require_api_key()):
    if api_key != ADMIN_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return True


@app.post('/world/characters')
def create_character(payload: dict, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO characters (name, age, traits, location_id, status) VALUES (?, ?, ?, ?, ?)', (
        payload.get('name'), payload.get('age'), str(payload.get('traits', {})), payload.get('location_id'), payload.get('status', 'alive')
    ))
    conn.commit()
    char_id = c.lastrowid
    conn.close()
    return {'status': 'created', 'id': char_id}


@app.put('/world/characters/{char_id}')
def update_character(char_id: int, payload: dict, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE characters SET name=?, age=?, traits=?, location_id=?, status=? WHERE id=?', (
        payload.get('name'), payload.get('age'), str(payload.get('traits', {})), payload.get('location_id'), payload.get('status'), char_id
    ))
    conn.commit()
    conn.close()
    return {'status': 'updated', 'id': char_id}


@app.delete('/world/characters/{char_id}')
def delete_character(char_id: int, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM characters WHERE id=?', (char_id,))
    conn.commit()
    conn.close()
    return {'status': 'deleted', 'id': char_id}


@app.post('/world/locations')
def create_location(payload: dict, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO locations (name, description, region, forbidden, locked, political_status, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)', (
        payload.get('name'), payload.get('description'), payload.get('region'), int(payload.get('forbidden', 0)), int(payload.get('locked', 0)), payload.get('political_status'), str(payload.get('metadata', {}))
    ))
    conn.commit()
    loc_id = c.lastrowid
    conn.close()
    return {'status': 'created', 'id': loc_id}


@app.put('/world/locations/{loc_id}')
def update_location(loc_id: int, payload: dict, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE locations SET name=?, description=?, region=?, forbidden=?, locked=?, political_status=?, metadata=? WHERE id=?', (
        payload.get('name'), payload.get('description'), payload.get('region'), int(payload.get('forbidden', 0)), int(payload.get('locked', 0)), payload.get('political_status'), str(payload.get('metadata', {})), loc_id
    ))
    conn.commit()
    conn.close()
    return {'status': 'updated', 'id': loc_id}


@app.delete('/world/locations/{loc_id}')
def delete_location(loc_id: int, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM locations WHERE id=?', (loc_id,))
    conn.commit()
    conn.close()
    return {'status': 'deleted', 'id': loc_id}


@app.post('/world/factions')
def create_faction(payload: dict, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', (
        payload.get('name'), payload.get('ideology'), str(payload.get('relationships', {}))
    ))
    conn.commit()
    fid = c.lastrowid
    conn.close()
    return {'status': 'created', 'id': fid}


@app.post('/world/factions/import')
def import_factions(payload: dict, admin: bool = Depends(require_admin)):
    """Bulk import faction names.

    Payload: { "names": ["Faction A", "Faction B", ...], "skip_existing": true }
    """
    names = payload.get('names') or []
    if not isinstance(names, list) or not names:
        raise HTTPException(status_code=400, detail='names list required')
    skip_existing = bool(payload.get('skip_existing', True))

    conn = get_connection()
    c = conn.cursor()
    inserted = 0
    for n in names:
        name = str(n).strip()
        if not name:
            continue
        if skip_existing:
            c.execute('SELECT id FROM factions WHERE name = ?', (name,))
            if c.fetchone():
                continue
        c.execute('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', (name, None, '{}'))
        inserted += 1
    conn.commit()
    conn.close()
    return {'status': 'imported', 'inserted': inserted}


@app.put('/world/factions/{fid}')
def update_faction(fid: int, payload: dict, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE factions SET name=?, ideology=?, relationships=? WHERE id=?', (
        payload.get('name'), payload.get('ideology'), str(payload.get('relationships', {})), fid
    ))
    conn.commit()
    conn.close()
    return {'status': 'updated', 'id': fid}


@app.delete('/world/factions/{fid}')
def delete_faction(fid: int, admin: bool = Depends(require_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM factions WHERE id=?', (fid,))
    conn.commit()
    conn.close()
    return {'status': 'deleted', 'id': fid}


from src.db.database import get_connection

@app.get("/world/state")
def get_world_state():
    conn = get_connection()
    try:
        state = assemble_world_state(conn)
    finally:
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


@app.get('/world/inventory/{owner_type}/{owner_id}')
def api_list_inventory(owner_type: str, owner_id: str, api_key: str = require_api_key()):
    rows = list_inventory(owner_type, owner_id)
    return rows


@app.post('/world/inventory/pickup')
def api_pickup_item(payload: dict, api_key: str = require_api_key()):
    owner_type = payload.get('owner_type')
    owner_id = str(payload.get('owner_id'))
    item_id = int(payload.get('item_id'))
    quantity = int(payload.get('quantity', 1))
    try:
        res = pickup_item(owner_type, owner_id, item_id, quantity)
        return {'status': 'ok', 'result': res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/world/inventory/{inventory_id}/use')
def api_use_inventory(inventory_id: int, payload: dict = {}, api_key: str = require_api_key()):
    quantity = int(payload.get('quantity', 1))
    try:
        res = use_inventory_item(inventory_id, quantity)
        return {'status': 'ok', 'result': res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/world/inventory/{inventory_id}/use_decision')
def api_use_inventory_decision(inventory_id: int, payload: dict = {}, api_key: str = require_api_key()):
    """Event-driven usage: create an `item_use` event, validate it, and apply consumption only if accepted.

    Payload should include `character_id` and optional `quantity`, `timestamp`, `metadata`.
    """
    character_id = payload.get('character_id')
    if not character_id:
        raise HTTPException(status_code=400, detail='character_id required')
    quantity = int(payload.get('quantity', 1))
    timestamp = payload.get('timestamp') or int(time.time())

    # Build an event representing the decision to use the item
    event = {
        'type': 'item_use',
        'character_id': str(character_id),
        'inventory_id': int(inventory_id),
        'quantity': quantity,
        'timestamp': timestamp,
        'metadata': payload.get('metadata', {})
    }

    # Validate with continuity rules
    is_valid, reason = validator.validate_event(event)
    if not is_valid:
        return {'status': 'rejected', 'reason': reason}

    # Apply consumption in a transaction
    try:
        res = use_inventory_item(inventory_id, quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Persist event to events table and publish
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO events (timestamp, type, description, involved_characters, involved_locations, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event.get('timestamp'),
        event.get('type'),
        f"character {character_id} used inventory {inventory_id}",
        str([character_id]),
        str([]),
        str(event.get('metadata', {}))
    ))
    conn.commit()
    conn.close()
    try:
        publisher.publish_event(event)
    except Exception:
        print('[ChronicleKeeper] Warning: failed to publish item_use event')

    # Apply event consumer side-effects (non-fatal)
    try:
        handle_event_consumer(event, db_conn_getter=get_connection)
    except Exception:
        print('[ChronicleKeeper] Warning: event consumer failed')

    return {'status': 'accepted', 'result': res}


@app.post('/world/inventory/{inventory_id}/equip')
def api_equip_inventory(inventory_id: int, payload: dict = {}, api_key: str = require_api_key()):
    slot = payload.get('slot')
    if not slot:
        raise HTTPException(status_code=400, detail='slot missing')
    try:
        res = equip_inventory_item(inventory_id, slot)
        return {'status': 'ok', 'result': res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
