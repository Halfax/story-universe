# Item & Inventory System — Design

Goals
- Flexible, extensible item model supporting: usable (consume/activate), wearable (equip to slots), carryable (inventory stackable), weapons, armor, eatable/drinkable (consumables).
- Simple persistence (SQLite) and efficient queries for inventory and equipped items.
- Support for gameplay-relevant properties: durability, weight, stack_size, charges, effects, damage/armor values.
- Clear API for engine and validator to ask: can this character use/equip/consume this item? Does it conflict with canon?

Core concepts
- Item (master record): canonical definition of an item type.
  - id (pk), sku (string unique), name, description
  - category: enum (weapon, armor, consumable, wearable, misc)
  - sub_type: free string (e.g., "sword", "helmet", "potion")
  - weight: float
  - stackable: bool
  - max_stack: int
  - equippable: bool
  - equip_slot: enum or list (head, torso, legs, hands, feet, neck, ring, back)
  - damage: optional (min, max, damage_type)
  - armor_rating: optional number
  - durability_max: optional int
  - consumable: bool
  - effects: JSON blob describing outcome of using/consuming (health +10, status "drunk", restore hunger)
  - charges: optional (max charges for rechargeable items)
  - tags: list (e.g., ["food","perishable","magical"]) for rules

- InventoryItem (instance record): an owned instance of an item or stack of items.
  - id (pk), owner_type ("character"/"container"), owner_id, item_id (FK -> Item), quantity, durability (for non-stackable), charges_remaining, equipped (bool), equip_slot, created_at
  - metadata JSON for custom fields (expiry timestamps, modifiers)

- Equip slots: fixed set; equipping enforces one item per slot per owner (or configurable multiple rings).

- Containers: optional (bags) that adjust capacity/weight. Model via `owner_type`/`owner_id` pointing to container records.

Database schema (high level)
- `items` table: stores master item types.
- `inventory` table: stores owned instances.
- `containers` optional table for bags (id, owner_type, owner_id, capacity, weight_mod)

Behavior rules & engine API
- get_inventory(owner_type, owner_id): returns inventory items, aggregated by item type when stackable.
- can_pickup(owner, item, quantity=1): checks weight capacity, stackability, rules.
- pickup_item(owner, item_id, qty): create or increment InventoryItem rows.
- can_equip(owner, inventory_item_id, slot): checks item equippable, slot free, character state (e.g., hands occupied, dead cannot equip).
- equip_item(owner, inventory_item_id, slot): set equipped flag, update equip_slot.
- use_item(owner, inventory_item_id): if consumable, apply effects, decrement quantity/charges, delete when exhausted.
- repair_durability(owner, inventory_item_id, amount): increment durability up to max.

Edge cases & considerations
- Stack splitting/merging when partially using stackable items.
- Durability on stackable vs non-stackable: typically durability for each instance (non-stackable); for stackable items we treat them as identical and degrade per use (or model as separate instances if needed).
- Race conditions: if multiple nodes can modify inventory, use DB transactions.
- Auditing: log ownership changes (who gave/took items) for canonical audit trail.
- Weight/encumbrance: compute total weight, cause movement penalties.

Integration with validator
- Continuity validator should check items in events involving items (e.g., `use_item`, `attack_with_item`): existence, ownership, equipped status, consumable/charges, and identity conflicts (e.g., using non-existent item id).

API surfaces to add
- CRUD for `items` (admin)
- Inventory endpoints for characters: `GET /world/characters/{id}/inventory`, `POST /world/characters/{id}/inventory/pickup`, `POST /world/characters/{id}/inventory/{inv_id}/use`, `POST /world/characters/{id}/inventory/{inv_id}/equip`

Next steps for implementation
1. Add DB tables: `items`, `inventory` (and optional `containers`).
2. Add Pydantic models in `shared/models/item.py`.
3. Add small service helpers in `chronicle-keeper/src/services/inventory.py` (pickup, use, equip logic with DB transactions).
4. Add admin CRUD endpoints and character-facing inventory endpoints.
5. Add unit tests for edge cases (stacking, equip conflicts, durability, consumption).

Implementation status (updates)
- Created `chronicle-keeper/src/db/schema.sql` additions for `items` and `inventory`.

Note: The repository layout was flattened on 2026-01-13. See [docs/REPO_LAYOUT_CHANGE.md](docs/REPO_LAYOUT_CHANGE.md).
- Added `shared/models/item.py` (dataclasses + helpers).
- Created package files `shared/__init__.py` and `shared/models/__init__.py` so models can be imported as `shared.models.item`.

Quick smoke test (run from repo root):
```powershell
# Using the Narrative Engine venv on Windows (example path)
C:\Users\arhal_iz5093n\Desktop\projects\story-universe\story-universe\narrative-engine\narrative-engine\venv\Scripts\Activate.ps1
python -c "import sys, os; sys.path.insert(0, os.path.abspath('.')); from shared.models.item import Item; print('Item imported:', Item.__name__)"
```

If you want, next I can add `chronicle-keeper/src/services/inventory.py` with transactional pickup/use/equip functions and corresponding unit tests.

API Endpoints (chronicle-keeper)
- **List inventory:** `GET /world/inventory/{owner_type}/{owner_id}` — returns inventory rows joined with item metadata.
- **Pickup item:** `POST /world/inventory/pickup` — payload: `{owner_type, owner_id, item_id, quantity}` — transactionally adds items to inventory (respects `stackable` and `max_stack`).
- **Use item:** `POST /world/inventory/{inventory_id}/use` — payload: `{quantity}` — consumes stackable/consumable items and returns `effects` payload (no automatic application to character state).
- **Equip item:** `POST /world/inventory/{inventory_id}/equip` — payload: `{slot}` — equips the item in the given slot, unequipping any other item in that slot for the owner.

Service notes
- The service functions live at `chronicle-keeper/src/services/inventory.py` and accept an optional `db_conn_getter` for testable in-memory DB usage.
- Effects stored in the `items.effects` JSON column are returned by the `use` operation but not automatically applied to character state — that integration belongs to the Narrative Engine or a higher-level Chronicle Keeper service.

Decision-driven usage flow
- Inventory consumption should be driven by an explicit decision/event from the character. The safe flow is:
  1. Client calls `POST /world/inventory/{inventory_id}/use_decision` with `{character_id, quantity, metadata?}`.
  2. Server constructs an `item_use` event and runs the `ContinuityValidator`.
  3. If the event is accepted, the server applies the consumption (transactionally) via the inventory service, persists the event to `events` and publishes it.
 4. If rejected, the server returns `{'status':'rejected','reason':...}` and no consumption occurs.

Notes:
- The existing `POST /world/inventory/{inventory_id}/use` endpoint remains available for direct/manual operations (admin or server-side workflows) but production character-driven usage should prefer the event-based `use_decision` endpoint.
- This design ensures all item-usage decisions are visible in the event timeline and subject to continuity validation and auditing.

Event consumer
- `chronicle-keeper/src/services/event_consumer.py` implements `handle_event(event, db_conn_getter=None)` which currently supports `item_use` events.
- When an `item_use` event is accepted and applied, the consumer reads the `items.effects` JSON, scales numeric effects by `quantity`, and upserts the character's canonical state into the new `character_state` table (recommended) under `character_id`.
- The consumer is called synchronously after `use_decision` to ensure effects are applied immediately and atomically with the event persistence.

DB helpers
- Use `chronicle-keeper/src/db/system_helpers.py` for convenient access to runtime state:
  - `get_system_value(key)`, `set_system_value(key, value)` — read/write system-level keys (e.g., `time`).
  - `get_character_state(character_id)`, `set_character_state(character_id, state)` — read/write per-character JSON state.

Example usage in services:
```py
from src.db.system_helpers import get_character_state, set_character_state

state = get_character_state(1)
state['hp'] = state.get('hp', 0) + 10
set_character_state(1, state)
```

Security & audit notes
- Applying effects via the event consumer ensures item usage is auditable and reversible (by inspecting event history) while keeping character state updates centralized in the `world_state` table.
 - Applying effects via the event consumer ensures item usage is auditable and reversible (by inspecting event history) while keeping character state updates centralized in the `character_state` table.

Terminology note
- `Item` = canonical type (static definition).
- `InventoryItem` = instance/stack owned by an actor.

Example minimal JSON for an item master record
```
{
  "sku": "potion_healing_small",
  "name": "Small Healing Potion",
  "category": "consumable",
  "sub_type": "potion",
  "weight": 0.5,
  "stackable": true,
  "max_stack": 10,
  "consumable": true,
  "effects": {"hp": 10}
}
```

Example InventoryItem
```
{
  "id": 123,
  "owner_type": "character",
  "owner_id": "1",
  "item_id": 42,
  "quantity": 3,
  "equipped": false,
  "metadata": {}
}
```
