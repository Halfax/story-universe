# Model Serialization / Deserialization

This document describes simple helpers added to shared models to convert between Python objects and dicts suitable for JSON persistence and DB storage.

Files modified:
- `shared/models/item.py` — added `Item.from_dict` and `InventoryItem.from_dict` to mirror existing `to_dict`.
- `shared/models/character.py` — added `to_dict` and `from_dict` helpers.
- `shared/models/event.py` — added `to_dict` and `from_dict` helpers for `Event` and `TickEvent`.

Guidelines:
- Use `to_dict()` when preparing objects for DB insertion or JSON responses.
- Use `from_dict()` when creating model instances from DB rows or incoming JSON.
- `from_dict()` implementations are defensive: they accept JSON-encoded strings for complex fields (e.g., `effects`, `tags`, `metadata`).

Example:

```py
from shared.models.item import Item
# create from DB row
row = {"id": 1, "sku": "potion_small", "name": "Small Potion", "effects": '{"hp": 10}', "tags": '["potion"]'}
item = Item.from_dict(row)
print(item.to_dict())
```

Notes:
- These helpers are intentionally small and keep data conversions explicit; the project also contains Pydantic-based `shared.models` for richer schemas where needed.

Note: The repository layout was flattened on 2026-01-13. See [docs/REPO_LAYOUT_CHANGE.md](docs/REPO_LAYOUT_CHANGE.md).
