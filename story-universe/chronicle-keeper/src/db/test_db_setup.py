import sqlite3
import os

def setup_test_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        type TEXT,
        description TEXT,
        involved_characters TEXT,
        involved_locations TEXT,
        metadata TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS world_state (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    conn.commit()
    conn.close()

def teardown_test_db(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
