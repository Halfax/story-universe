# Continuity Validator

Overview
--------
The `ContinuityValidator` enforces world-consistency rules before events
are applied. It prevents contradictions, enforces timeline ordering, validates
cross-entity references, and applies narrative-aware constraints (lore/physics/politics).

Location
--------
Implementation: [src/services/continuity.py](src/services/continuity.py#L1-L1360)

Key Capabilities
----------------
- Identity and state checks: prevent impossible state transitions (e.g., dead→alive),
  and detect identity/name contradictions.
- Timeline checks: reject retroactive events (per-character and per-location)
  by inspecting `recent_events` timestamps.
- Cross-entity validation: ensures referenced characters, factions, and locations
  exist (in-memory or via DB lookups when configured).
- Relationship rules: enforce alliance/enemy/rival constraints, cooldowns and
  trust-based gating for diplomatic/aggressive actions.
- Narrative constraints: lore-based checks (magic/physics/politics) to block
  actions not allowed by character traits or location metadata.
- Causation/correlation checks: verifies `causationId` presence and timestamp
  ordering; detects contradictory actions within the same `correlationId`.
- Performance: lightweight in-memory cache (`cache_ttl`) to avoid repeated DB reads
  during bursts of validations.

Usage
-----
Create an instance with an injected `db_conn_getter` for DB-backed validation
or pass a minimal `world_state` dict for fast, test-friendly validation:

```python
from services.continuity import ContinuityValidator

# test mode
cv = ContinuityValidator(world_state=test_state)
ok, reason = cv.validate_event(event)

# production mode (provide a callable returning a DB connection)
cv = ContinuityValidator(db_conn_getter=get_connection)
ok, reason = cv.validate_event(event)
```

Extending rules
----------------
- Add event-type-specific constraints inside `validate_event`.
- For heavy-weight checks (cross-table consistency, historical queries), prefer
  writing small DB-backed helper functions and keep `validate_event` fast.

Operational notes
-----------------
- Tune `cache_ttl` when constructing `ContinuityValidator` to balance freshness
  vs. DB load (defaults to 5 seconds).
- For deterministic behavior in tests, pass a fixed `world_state` and avoid
  injecting `db_conn_getter`.

Testing
-------
Existing unit tests live in `tests/test_continuity.py` and
`tests/test_continuity_relationships.py`. They exercise timeline checks,
relationship gating, and narrative constraints.

Changelog
---------
- 2026-01-13: Documentation added and continuity validator reviewed. All
  sub-items (validation rules, timeline checks, narrative constraints,
  and basic performance cache) present in implementation.
