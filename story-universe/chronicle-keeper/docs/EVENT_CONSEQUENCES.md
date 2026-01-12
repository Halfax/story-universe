Event Consequences and State Updates

Purpose
- Describe how accepted events should update canonical state (DB) so future validations and the generator see consistent world changes.

Basic consequence rules
- `character_action` with `action=move`: update the `characters.location_id` field.
- `character_state_change`: update `characters.status` (alive/dead/missing) and record the change in `character_state`/`character_history` tables.
- `faction_event` actions:
  - `attack`: optionally modify `faction_metrics.resources`/`power` and set `faction_relationships.strength` lower (more negative).
  - `form_alliance`: create/update `faction_relationships` rows with `relationship_type='ally'` and set cooldown `form_alliance` on the source faction.
  - `betray`: flip or adjust `relationship_type`/`strength` accordingly and set `cooldown_until` on the relationship.

Implementation notes
- The API ingest path should call `apply_event_consequences(event, db_conn)` after the event is accepted by the validator.
- Consequence application must be idempotent for duplicate-event protection; use event `id` or canonical fingerprint to avoid re-applying side-effects.
- Consequences should be wrapped in a DB transaction and commit only after all related updates succeed.
- Track change provenance via `events` table `metadata` and include `applied_by`/`applied_ts` where appropriate.
