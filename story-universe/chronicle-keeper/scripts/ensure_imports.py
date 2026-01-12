#!/usr/bin/env python3
"""Ensure factions and items are imported into the Chronicle Keeper DB.

Behavior:
- If environment `CHRONICLE_AUTO_IMPORT` is truthy ("1","true","yes") this
  script will attempt imports for both tables if CSVs are present.
- Otherwise it will only import when the corresponding table is empty.

This is intended to be run from the container entrypoint on startup.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = ROOT / 'data'
FACTION_CSV = os.environ.get('CHRONICLE_FACTION_CSV') or str(CSV_DIR / 'faction_names.csv')
ITEMS_CSV = os.environ.get('CHRONICLE_ITEMS_CSV') or str(CSV_DIR / 'items.csv')

def truthy(v):
    if not v:
        return False
    return str(v).lower() in ('1', 'true', 'yes', 'on')

def table_count(conn, table):
    c = conn.cursor()
    try:
        c.execute(f'SELECT COUNT(1) FROM {table}')
        return c.fetchone()[0]
    except Exception:
        return None

def run_import(script, csv_path):
    if not Path(csv_path).exists():
        print(f'SKIP: CSV not found: {csv_path}')
        return False
    cmd = [sys.executable, script, '--csv', csv_path, '--commit']
    print('Running:', ' '.join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    return p.returncode == 0

def main():
    # import DB helper
    try:
        proj_root = Path(__file__).resolve().parents[1]
        if str(proj_root) not in sys.path:
            sys.path.insert(0, str(proj_root))
        from src.db.database import get_connection
    except Exception as e:
        print('Failed to import DB helper:', e)
        return 2

    conn = get_connection()

    auto_mode = truthy(os.environ.get('CHRONICLE_AUTO_IMPORT'))
    print('Auto-import mode:', auto_mode)

    faction_count = table_count(conn, 'factions')
    item_count = table_count(conn, 'items')
    print('Existing counts: factions=', faction_count, 'items=', item_count)

    # Decide whether to run
    ran_any = False

    # Factions
    if auto_mode or (faction_count is not None and faction_count == 0):
        print('Attempting faction import...')
        if run_import(str(Path(__file__).parent / 'import_factions.py'), FACTION_CSV):
            ran_any = True
    else:
        print('Skipping faction import (not empty or disabled).')

    # Items
    if auto_mode or (item_count is not None and item_count == 0):
        print('Attempting item import...')
        if run_import(str(Path(__file__).parent / 'import_items.py'), ITEMS_CSV):
            ran_any = True
    else:
        print('Skipping item import (not empty or disabled).')

    conn.close()
    return 0 if ran_any else 0

if __name__ == '__main__':
    sys.exit(main())
