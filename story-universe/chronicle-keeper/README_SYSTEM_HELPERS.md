Chronicle Keeper — `system_helpers` quick guide

Overview
- `chronicle-keeper/src/db/system_helpers.py` provides convenience helpers for reading/writing runtime state:
  - `system_state` — global key/value pairs (e.g., `time`)
  - `character_state` — per-character JSON blobs (runtime HP, buffs, cooldowns)

Helpers
- `get_system_value(key) -> Optional[str]`
- `set_system_value(key, value)`
- `get_character_state(character_id) -> Dict`
- `set_character_state(character_id, state_dict)`

Example (apply consumable effects):
```py
from src.db.system_helpers import get_character_state, set_character_state

state = get_character_state(1)
state['hp'] = state.get('hp', 0) + 10
set_character_state(1, state)
```

CLI
You can quickly inspect a character state with Python:
```powershell
python -c "import sys, os; sys.path.insert(0, os.path.abspath('.')); from src.db.system_helpers import get_character_state; print(get_character_state(1))"
```

Notes
- Helpers use `db_conn_getter` optional parameter for in-memory testing.
- These helpers are intentionally small — higher-level domain logic should live in services.
