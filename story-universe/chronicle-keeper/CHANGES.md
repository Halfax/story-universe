Chronicle Keeper — Change Log

2026-01-12
- Added enhanced faction schema and runtime tables: `faction_members`, `faction_state`, `faction_metrics`.
- Validator (`src/services/continuity.py`) now loads `faction_metrics` and exposes `metrics.trust` to validation logic.
- New validation rules: low-trust factions cannot form alliances; extremely low-trust factions are prevented from initiating coordinated attacks.
- API endpoints added:
  - `GET /world/factions/{id}/metrics` — fetch `trust`, `power`, `resources`, `influence` for a faction (defaults if missing).
  - `PUT /world/factions/{id}/metrics` — partial update/upsert for faction metrics.

Notes:
- Schema migration in `src/db/schema.sql` preserves the old `factions` table where possible and migrates to the enhanced schema.
- Next work: wire `trust` into generator weighting; add unit tests for validator rules; add a CSV importer step to seed metrics where appropriate.

2026-01-13
- Add `event_consequences` table to schema to persist compact undo payloads for reversible event consequences. `apply_event_consequences` may insert into this table when events include `reversible=true` and have an `id`. This table is created by `src/db/schema.sql` and ensured during `src/db/init_db.py` initialization (and therefore created when the Docker image runs the DB initializer).
