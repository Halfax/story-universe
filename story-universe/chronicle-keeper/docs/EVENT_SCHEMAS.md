# Event Schemas

This document describes the canonical event structure used by Chronicle Keeper.

Minimal canonical event fields (validated by `CanonicalEvent` Pydantic/model):

- `id` (string): unique event identifier. If not provided, the API will generate one.
- `type` (string): event type, e.g. `character_action`, `character_state_change`, `faction_event`, `character_create`, etc.
- `timestamp` (int, optional): UNIX timestamp of the event.
- `description` (string, optional): human-friendly summary.
- `data` (object, optional): free-form payload for event-specific fields.
- `involved_characters` (list): character IDs referenced by the event.
- `involved_locations` (list): location IDs referenced by the event.
- `metadata` (object): protocol metadata. Common keys:
  - `causationId`: id of the event that directly caused this event
  - `correlationId`: id grouping related events into an arc or transaction

Common `type`-specific fields (examples):

- `character_action`:
  - `character_id` (int)
  - `action` (string)
  - `location_id` (int, optional)
  - `target_id` (int, optional)

- `character_state_change`:
  - `character_id` (int)
  - `new_status` (string)

- `faction_event`:
  - `source_faction_id` (int)
  - `target_faction_id` (int, optional)
  - `action` (string) e.g. `attack`, `form_alliance`, `betray`
  - `severity` (float 0.0-1.0, optional)
  - `stability` (float 0.0-1.0, optional)

Notes:
- The `CanonicalEvent` model enforces required types and basic constraints. The continuity validator performs lore- and state-aware validation that cannot be covered by a pure schema (e.g., "cannot attack ally").
- Keep `metadata.causationId` and `metadata.correlationId` consistent across event arcs to allow tracking and rejection of invalid follow-ups.

See `EVENT_VALIDATION.md` for details on validation rules applied at ingest.
