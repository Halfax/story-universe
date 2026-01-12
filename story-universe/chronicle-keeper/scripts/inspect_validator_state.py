from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'universe.db'

try:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from src.services.continuity import ContinuityValidator
    from src.db.database import get_connection
except Exception as e:
    print('Import failed:', e)
    raise

v = ContinuityValidator(db_conn_getter=get_connection)
# show the DB path used by the db helper
import src.db.database as _dbmod
print('Database module DB_PATH:', getattr(_dbmod, 'DB_PATH', None))
try:
    state = v._load_state_from_db()
    print('Loaded factions keys:', list(state.get('factions', {}).keys())[:10])
    for fid, info in state.get('factions', {}).items():
        print('Faction', fid, 'name=', info.get('name'), 'metrics=', info.get('metrics'))
except Exception as e:
    import traceback
    print('Error while loading state:')
    traceback.print_exc()
