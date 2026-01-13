# Arc Persistence

This document describes the simple SQLite-backed arc persistence used by the Narrative Engine.

- Schema: `src/db/schema_arcs.sql` — table `arcs` with columns:
  - `id` (TEXT PK)
  - `name` (TEXT)
  - `state` (TEXT)
  - `created_at` / `updated_at` (ISO timestamps)
  - `participants` (JSON array of character ids)
  - `events` (JSON array of event objects)
  - `goals` (JSON array describing arc goals)
  - `data` (JSON object for additional payload)

- API: `services.arc_persistence` provides `init_db`, `create_arc`, `get_arc`, `list_arcs`, `update_arc`, `delete_arc`.

- Usage example in `narrative-engine/src/event_generator.py`:

  - Instantiate `NarrativeEngine(..., db_path="/path/to/db.sqlite")` to enable automatic schema initialization and arc loading.
  - `create_arc()` will persist a new arc; `advance_arc()` will update the arc's events and state.

Notes:
- The persistence layer stores JSON blobs; queries are simple and intended for deterministic tests and small deployments. For production, consider adding indices, event pagination, and event normalization.
