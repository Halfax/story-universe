"""Simple SQLite-backed persistence for story arcs.

This module provides a minimal, testable CRUD surface for story arcs.
Arcs are stored as JSON blobs to keep the schema flexible while enabling
queries by `id`, `name`, and timestamps.
"""
from __future__ import annotations

import json
import sqlite3
import os
from typing import Any, Dict, List, Optional
from datetime import datetime


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'schema_arcs.sql'))
    with open(schema_path, 'r', encoding='utf-8') as fh:
        script = fh.read()
    with conn:
        cur.executescript(script)
    conn.close()


def create_arc(db_path: str, arc: Dict[str, Any]) -> None:
    now = _now_iso()
    arc_record = {
        'id': arc['id'],
        'name': arc.get('name', ''),
        'state': arc.get('state', 'pending'),
        'created_at': arc.get('created_at', now),
        'updated_at': now,
        'participants': json.dumps(arc.get('participants', [])),
        'events': json.dumps(arc.get('events', [])),
        'goals': json.dumps(arc.get('goals', [])),
        'data': json.dumps(arc.get('data', {})),
    }
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO arcs (id, name, state, created_at, updated_at, participants, events, goals, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                arc_record['id'],
                arc_record['name'],
                arc_record['state'],
                arc_record['created_at'],
                arc_record['updated_at'],
                arc_record['participants'],
                arc_record['events'],
                arc_record['goals'],
                arc_record['data'],
            ),
        )
    conn.close()


def get_arc(db_path: str, arc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM arcs WHERE id = ?", (arc_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'id': row['id'],
        'name': row['name'],
        'state': row['state'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
        'participants': json.loads(row['participants'] or '[]'),
        'events': json.loads(row['events'] or '[]'),
        'goals': json.loads(row['goals'] or '[]'),
        'data': json.loads(row['data'] or '{}'),
    }


def list_arcs(db_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    q = "SELECT * FROM arcs ORDER BY created_at DESC"
    if limit:
        q += " LIMIT ?"
        cur.execute(q, (limit,))
    else:
        cur.execute(q)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            'id': r['id'],
            'name': r['name'],
            'state': r['state'],
            'created_at': r['created_at'],
            'updated_at': r['updated_at'],
            'participants': json.loads(r['participants'] or '[]'),
            'events': json.loads(r['events'] or '[]'),
            'goals': json.loads(r['goals'] or '[]'),
            'data': json.loads(r['data'] or '{}'),
        }
        for r in rows
    ]


def update_arc(db_path: str, arc_id: str, updates: Dict[str, Any]) -> bool:
    arc = get_arc(db_path, arc_id)
    if not arc:
        return False
    arc['name'] = updates.get('name', arc['name'])
    arc['state'] = updates.get('state', arc['state'])
    # merge participants/events/goals/data when present
    if 'participants' in updates:
        # replace participants list
        arc['participants'] = updates['participants']
    if 'events' in updates:
        arc['events'] = updates['events']
    if 'goals' in updates:
        arc['goals'] = updates['goals']
    arc['data'].update(updates.get('data', {}))
    arc['updated_at'] = _now_iso()
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "UPDATE arcs SET name = ?, state = ?, updated_at = ?, participants = ?, events = ?, goals = ?, data = ? WHERE id = ?",
            (
                arc['name'],
                arc['state'],
                arc['updated_at'],
                json.dumps(arc.get('participants', [])),
                json.dumps(arc.get('events', [])),
                json.dumps(arc.get('goals', [])),
                json.dumps(arc['data']),
                arc_id,
            ),
        )
    conn.close()
    return True


def delete_arc(db_path: str, arc_id: str) -> bool:
    conn = get_connection(db_path)
    with conn:
        cur = conn.execute("DELETE FROM arcs WHERE id = ?", (arc_id,))
        deleted = cur.rowcount
    conn.close()
    return deleted > 0
