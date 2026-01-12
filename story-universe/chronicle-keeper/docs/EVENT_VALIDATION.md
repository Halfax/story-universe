# Event Validation

Chronicle Keeper validates events at two levels:

1. Schema-level validation (Pydantic / `CanonicalEvent`):
   - Ensures fields are present and of the correct type.
   - Rejects immediately malformed payloads (response: `{status: 'rejected', reason: 'schema validation failed: ...'}`).

2. Continuity validation (`ContinuityValidator.validate_event`):
   - Loads canonical world state from the DB (if configured) or uses in-memory `world_state` for tests.
   - Enforces identity and timeline constraints (no retroactive timestamps, no resurrection without explicit flow).
   - Enforces character constraints (dead characters cannot act; protected characters cannot be attacked).
   - Enforces faction rules: relationship-type constraints, trust thresholds, numeric relationship strengths, and cooldowns.
   - Validates `metadata.causationId` / `metadata.correlationId` chains to ensure follow-ups reference valid prior events.

Behavior at ingest (`POST /event`):
- If schema validation fails: request returns HTTP 200 with `{status: 'rejected', reason: ...}` to preserve legacy behavior.
- If continuity validation fails: request returns HTTP 200 with `{status: 'rejected', reason: ...}`.
- If accepted: event is persisted in the `events` table and published via the TickPublisher.

Extending rules:
- Add new lore constraints in `ContinuityValidator.validate_event` near the `# 9. Lore-aware validation` section.
- For DB-backed checks, prefer using the injected `db_conn_getter` for testability.

Testing:
- Unit tests should exercise both schema and continuity checks. Use a test DB (`test_chronicle.db`) or provide `world_state` to `ContinuityValidator` to avoid background services.

