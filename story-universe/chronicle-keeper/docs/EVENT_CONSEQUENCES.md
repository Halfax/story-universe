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

Extended behavior (2026-01-13)
- Multi-target consequences: `apply_event_consequences` supports `target_faction_ids` (list or CSV) as well as the single `target_faction_id`. When present, consequences are partitioned and applied to each listed target.
- Reversible consequences: Events may include `metadata.reversible=true` or top-level `reversible=true`. When an event has an `id` and is reversible, a compact undo payload is stored in a new `event_consequences` table (`event_id`, `reversible`, `undo_payload`, `applied_ts`) so callers can inspect or attempt reversal.
- Persona / Faction-aware scaling: `severity` and `stability` fields are parsed and clamped to safe ranges; persona drift scales by `severity` (aggressive actions) or `stability` (alliances). Very large values are logged as warnings.
- Sanity checks: `severity`/`stability` are sanitized and clamped to [-1.0, 1.0]. Large magnitudes are warned. Alliance/attack gating remains enforced by trust/relationship existence and cooldowns.

Notes on reversibility
- The undo payload contains a snapshot of the most important pre-change values (relationship row, trust metrics, personality_traits) for each affected target. It is a best-effort, compact representation intended to allow operator-driven reversal or analysis; full transactional rollback is still recommended if strict atomicity is required.
