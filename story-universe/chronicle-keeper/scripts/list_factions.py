import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'universe.db'
print('DB:', DB)
conn = sqlite3.connect(str(DB))
c = conn.cursor()
c.execute('SELECT id, name FROM factions')
rows = c.fetchall()
print('Factions rows:', rows)
conn.close()
