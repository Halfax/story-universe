"""Quick test: insert a faction with low trust and assert validator rejects alliance formation."""
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'universe.db'

def ensure_faction(conn, name, trust=0.1):
    c = conn.cursor()
    c.execute('SELECT id FROM factions WHERE name = ?', (name,))
    row = c.fetchone()
    if row:
        fid = row[0]
    else:
        c.execute('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', (name, None, '{}'))
        fid = c.lastrowid
    c.execute('SELECT faction_id FROM faction_metrics WHERE faction_id = ?', (fid,))
    if not c.fetchone():
        c.execute('INSERT INTO faction_metrics (faction_id, trust, power, resources, influence) VALUES (?, ?, ?, ?, ?)', (fid, float(trust), 1, 10, 0))
    else:
        c.execute('UPDATE faction_metrics SET trust = ? WHERE faction_id = ?', (float(trust), fid))
    conn.commit()
    return fid

def run_test():
    conn = sqlite3.connect(str(DB))
    fid = ensure_faction(conn, 'LowTrustFaction', trust=0.05)
    # ensure at least one character exists so validator does not fall back to minimal default
    c = conn.cursor()
    c.execute('SELECT id FROM characters LIMIT 1')
    if not c.fetchone():
        c.execute('INSERT INTO characters (name, age, traits, location_id, status) VALUES (?, ?, ?, ?, ?)', ('Dummy', 30, '[]', None, 'alive'))
        conn.commit()
    conn.close()

    # Run validator
    try:
        proj_root = ROOT
        if str(proj_root) not in sys.path:
            sys.path.insert(0, str(proj_root))
        from src.services.continuity import ContinuityValidator
        from src.db.database import get_connection
    except Exception as e:
        print('Import failed:', e)
        return 2

    validator = ContinuityValidator(db_conn_getter=get_connection)
    event = {'type': 'faction_event', 'source_faction_id': fid, 'target_faction_id': fid, 'action': 'form_alliance'}
    valid, reason = validator.validate_event(event)
    print('Validator result:', valid, reason)
    return 0 if not valid else 1

if __name__ == '__main__':
    exit(run_test())
