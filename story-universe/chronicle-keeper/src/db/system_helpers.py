"""Helpers for reading/writing `system_state` and `character_state`.

Small convenience functions used by services to fetch/update global
runtime keys (e.g., `time`) and per-character runtime JSON blobs.
"""
from typing import Any, Optional, Dict
import json


def _get_conn(db_conn_getter=None):
    if db_conn_getter:
        return db_conn_getter()
    from src.db.database import get_connection
    return get_connection()


def get_system_value(key: str, db_conn_getter=None) -> Optional[str]:
    conn = _get_conn(db_conn_getter)
    cur = conn.cursor()
    cur.execute("SELECT value FROM system_state WHERE key=?", (key,))
    row = cur.fetchone()
    try:
        if db_conn_getter is None:
            conn.close()
    except Exception:
        pass
    return row[0] if row else None


def set_system_value(key: str, value: Any, db_conn_getter=None):
    conn = _get_conn(db_conn_getter)
    cur = conn.cursor()
    cur.execute("REPLACE INTO system_state (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    try:
        if db_conn_getter is None:
            conn.close()
    except Exception:
        pass


def get_character_state(character_id: int, db_conn_getter=None) -> Dict[str, Any]:
    conn = _get_conn(db_conn_getter)
    cur = conn.cursor()
    cur.execute("SELECT state FROM character_state WHERE character_id=?", (int(character_id),))
    row = cur.fetchone()
    try:
        if row and row[0]:
            return json.loads(row[0])
    except Exception:
        pass
    finally:
        try:
            if db_conn_getter is None:
                conn.close()
        except Exception:
            pass
    return {}


def set_character_state(character_id: int, state: Dict[str, Any], db_conn_getter=None):
    conn = _get_conn(db_conn_getter)
    cur = conn.cursor()
    cur.execute("REPLACE INTO character_state (character_id, state, last_updated) VALUES (?, ?, ?)", (int(character_id), json.dumps(state), int(__import__('time').time())))
    conn.commit()
    try:
        if db_conn_getter is None:
            conn.close()
    except Exception:
        pass
