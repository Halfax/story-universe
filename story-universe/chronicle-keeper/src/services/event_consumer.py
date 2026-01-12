import json
from typing import Optional, Callable, Any, Dict


def _get_conn(db_conn_getter: Optional[Callable[[], Any]] = None):
    if db_conn_getter:
        return db_conn_getter()
    from src.db.database import get_connection
    return get_connection()


def handle_event(event: Dict[str, Any], db_conn_getter: Optional[Callable[[], Any]] = None) -> Optional[Dict[str, Any]]:
    """Handle incoming events and apply side effects to canonical state.

    Currently supports `item_use` events by applying `items.effects` to
    a character's state stored in the dedicated `character_state` table
    (recommended: `character_state.state` contains a JSON blob for per-character runtime state).
    """
    try:
        etype = event.get('type')
        if etype == 'item_use' or etype == 'item_use_decision' or etype == 'item_use':
            return _apply_item_use_effects(event, db_conn_getter=db_conn_getter)
        # Other event types can be handled here
        return None
    except Exception:
        # Non-fatal: log where appropriate
        import traceback
        traceback.print_exc()
        return None


def _apply_item_use_effects(event: Dict[str, Any], db_conn_getter: Optional[Callable[[], Any]] = None) -> Dict[str, Any]:
    conn = _get_conn(db_conn_getter)
    cur = conn.cursor()

    inventory_id = int(event.get('inventory_id'))
    character_id = str(event.get('character_id'))
    quantity = int(event.get('quantity', 1))

    # Load inventory and item
    cur.execute('SELECT i.*, it.effects FROM inventory i JOIN items it ON i.item_id = it.id WHERE i.id=?', (inventory_id,))
    row = cur.fetchone()
    if not row:
        return {}

    # effects may be stored in items.effects (JSON string)
    # Depending on cursor/row shape, index name may differ; handle by column name if available
    try:
        effects_raw = row["effects"]
    except Exception:
        # fallback: last column
        effects_raw = row[-1]

    effects = json.loads(effects_raw or "{}") if effects_raw else {}

    # Multiply numeric effects by quantity
    computed = {}
    for k, v in effects.items():
        if isinstance(v, (int, float)):
            computed[k] = v * quantity
        else:
            computed[k] = v

    # Load existing character state from `character_state` table
    cur.execute('SELECT state FROM character_state WHERE character_id=?', (int(character_id),))
    row = cur.fetchone()
    if row and row[0]:
        try:
            state = json.loads(row[0])
        except Exception:
            state = {}
    else:
        state = {}

    # Apply computed effects to state
    for k, v in computed.items():
        if isinstance(v, (int, float)):
            state[k] = state.get(k, 0) + v
        else:
            state[k] = v

    # Persist back to world_state (upsert)
    value = json.dumps(state)
    import time
    ts = int(time.time())
    cur.execute('INSERT OR REPLACE INTO character_state (character_id, state, last_updated) VALUES (?, ?, ?)', (int(character_id), value, ts))
    conn.commit()

    return state
