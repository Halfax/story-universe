# DB initialization script for Chronicle Keeper (for Docker automation)
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "universe.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    # Ensure character_state, system_state and events tables exist for automation
    conn.execute(
        """CREATE TABLE IF NOT EXISTS character_state (
        character_id INTEGER PRIMARY KEY,
        state TEXT,
        last_updated INTEGER,
        FOREIGN KEY(character_id) REFERENCES characters(id)
    )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS system_state (
        key TEXT PRIMARY KEY,
        value TEXT
    )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        type TEXT,
        description TEXT,
        involved_characters TEXT,
        involved_locations TEXT,
        metadata TEXT
    )"""
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
