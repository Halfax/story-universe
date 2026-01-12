# SQLite/DuckDB connection helpers for Chronicle Keeper

import sqlite3
from pathlib import Path

import os
DB_PATH = os.environ.get("CHRONICLE_KEEPER_DB_PATH")
if not DB_PATH:
    DB_PATH = Path(__file__).parent.parent.parent / 'universe.db'

def get_connection():
    return sqlite3.connect(DB_PATH)
