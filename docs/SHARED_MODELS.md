# Shared Models

This document summarizes the current small, canonical shared models used across the repository and their intended responsibilities.

Files:

- `shared/models/item.py` — `Item`, `InventoryItem`, equip helpers, and `apply_consumable_effects`.
- `shared/models/character.py` — `Character` dataclass with attributes, traits, inventory ids, and `apply_delta()`.
- `shared/models/faction.py` — `Faction` dataclass with attributes and relationship map and `apply_delta()`.
- `shared/models/inventory_service.py` — basic inventory mutation helpers: `add_item_to_inventory`, `use_inventory_item`, `equip_inventory_item`, `unequip_inventory_item`.

Current coverage:

- Add missing fields: Basic fields for `Item`, `InventoryItem`, `Character`, and `Faction` are present. They are minimal but cover common fields like ids, names, attributes, traits, timestamps, inventory references, and basic equip/consumable metadata.

- Schema validation: Pydantic schemas were added and JSON Schema files were generated to `docs/schemas/`.
- Files generated:
	- `docs/schemas/item.schema.json`
	- `docs/schemas/inventory_item.schema.json`
	- `docs/schemas/character.schema.json`
	- `docs/schemas/faction.schema.json`
  
	Use these schemas for request/response validation or to generate API docs. Runtime model implementations now use Pydantic:

- The implementation-compatible wrappers live in `shared/models/item.py`, `shared/models/character.py`, and `shared/models/faction.py` and subclass the Pydantic models in `shared/models/schemas.py`.
- They provide `to_dict()` / `from_dict()` and `apply_delta()` compatibility methods so existing calling code should continue to work while benefiting from runtime validation.

For stricter behavior you may import the underlying Pydantic types directly from `shared/models/schemas.py`.

- Character/Faction state deltas: `Character.apply_delta()` and `Faction.apply_delta()` exist to apply numeric and simple deltas to attributes in-place. These are small helpers intended for the Continuity Engine to call with consequence deltas.

- Inventory mutation rules: `inventory_service` implements minimal mutation helpers for adding, using, equipping, and unequipping items. These helpers are intentionally lightweight: persistence and enforcement of cross-entity constraints (e.g., owner existence, stack merging, concurrent updates) should be implemented at the caller/service level (chronicle-keeper service).

Recommendations / Next steps:

- Add strict schema validation (pydantic or jsonschema) for public-facing APIs and event payload validation.

Note: The repository layout was flattened on 2026-01-13. See [docs/REPO_LAYOUT_CHANGE.md](docs/REPO_LAYOUT_CHANGE.md).
- Add transactional inventory operations inside `chronicle-keeper/src/services/inventory.py` that call these helpers and handle DB persistence, concurrency, and audits.
- Add unit tests for `shared/models` covering serialization roundtrips, `apply_delta()` semantics, and inventory mutation edge cases (zero charges, durability depletion, equip slot conflicts).

If you want, I can:

- Convert these models to `pydantic` and add JSON schemas.
- Implement a small `chronicle-keeper` inventory service layer that persists inventory changes and enforces rules.
- Add unit tests and CI entries for the new tests.

Tell me which of the above you'd like me to do next.
