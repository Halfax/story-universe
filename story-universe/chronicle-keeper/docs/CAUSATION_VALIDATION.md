Causation & Correlation Validation

Purpose
- Ensure incoming events that cite `causationId` or `correlationId` reference valid prior events and that preconditions are satisfied before accepting dependent events.

Rules
- If `event.metadata.causationId` is present, the validator will verify the referenced event exists in the recent events cache or in the `events` table.
- If the causation event is missing, the incoming event is rejected as missing preconditions.
- Correlation (`correlationId`) is advisory for grouping; the validator will not reject on correlation alone but may use correlation chains for arc consistency checks.
- If a causation event exists but its type/metadata implies a state change (e.g., character death), ensure preconditions for the dependent event are met (character still alive, location exists, etc.).

Implementation notes
- The validator provides `_validate_causation_chain(event)` which performs DB-backed lookup when a `db_conn_getter` is available, otherwise checks the in-memory `recent_events` list.
- For performance, the lookup first checks `recent_events` (in-memory), then queries `events` by `id`.
- Tuning: optionally allow a grace-window where a causation event may be missing if the source is known to be an external system (configurable).
