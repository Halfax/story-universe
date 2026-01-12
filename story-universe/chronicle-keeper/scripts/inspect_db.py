import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'universe.db'
print('DB path:', DB)
conn = sqlite3.connect(str(DB))
c = conn.cursor()
print('\nTables:')
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for r in c.fetchall():
    print(' -', r[0])

print('\nSchema for faction_metrics (if present):')
try:
    c.execute("PRAGMA table_info('faction_metrics')")
    rows = c.fetchall()
    if not rows:
        print('  (no faction_metrics table found)')
    else:
        for col in rows:
            print('  ', col)
except Exception as e:
    print('  error inspecting faction_metrics:', e)

conn.close()
