# SQLite/DuckDB connection helpers for Chronicle Keeper

import sqlite3
from pathlib import Path

import os


def _default_db_path():
    return Path(__file__).parent.parent.parent / "universe.db"


def get_connection():
    db_path = os.environ.get("CHRONICLE_KEEPER_DB_PATH")
    if not db_path:
        db_path = _default_db_path()
    return sqlite3.connect(db_path)
