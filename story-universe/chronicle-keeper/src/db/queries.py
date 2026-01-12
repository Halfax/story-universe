# Query helpers for Chronicle Keeper DB

def get_latest_events(conn, limit=50):
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
    return c.fetchall()

def get_world_state(conn):
    import sqlite3
    c = conn.cursor()
    # Assemble a useful world-state snapshot from canonical tables
    state = {}
    # Characters
    try:
        c.execute("SELECT id, name, age, traits, location_id, status FROM characters")
        chars = {}
        for row in c.fetchall():
            cid = str(row[0])
            chars[cid] = {
                'id': row[0],
                'name': row[1],
                'age': row[2],
                'traits': row[3],
                'location_id': row[4],
                'status': row[5]
            }
        state['characters'] = chars
    except sqlite3.OperationalError:
        state['characters'] = {}

    # Locations
    try:
        c.execute("SELECT id, name, description, region, forbidden, locked, political_status, metadata FROM locations")
        locs = {str(r[0]): {'id': r[0], 'name': r[1], 'description': r[2], 'region': r[3], 'forbidden': bool(r[4]), 'locked': bool(r[5]), 'political_status': r[6], 'metadata': r[7]} for r in c.fetchall()}
        state['locations'] = locs
    except sqlite3.OperationalError:
        state['locations'] = {}

    # Factions
    try:
        c.execute("SELECT id, name, ideology, relationships FROM factions")
        facs = {str(r[0]): {'id': r[0], 'name': r[1], 'ideology': r[2], 'relationships': r[3]} for r in c.fetchall()}
        state['factions'] = facs
    except sqlite3.OperationalError:
        state['factions'] = {}

    # Per-character runtime state
    try:
        c.execute("SELECT character_id, state FROM character_state")
        runtime = {str(r[0]): r[1] for r in c.fetchall()}
        state['character_state'] = runtime
    except sqlite3.OperationalError:
        state['character_state'] = {}

    # System-level values (e.g., time)
    try:
        c.execute("SELECT key, value FROM system_state")
        system = {r[0]: r[1] for r in c.fetchall()}
        state['system'] = system
    except sqlite3.OperationalError:
        state['system'] = {}

    return state
