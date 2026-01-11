# Query helpers for Chronicle Keeper DB

def get_latest_events(conn, limit=50):
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
    return c.fetchall()

def get_world_state(conn):
    c = conn.cursor()
    c.execute("SELECT key, value FROM world_state")
    return {row[0]: row[1] for row in c.fetchall()}
