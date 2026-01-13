# Narrative Engine — Arc Weighting Integration

This document describes how the Narrative Engine uses the DB-backed arc-goal
weighting when a `db_path` is provided to the engine.

How to enable
- Instantiate the engine with `db_path` pointing to an SQLite file initialized with `src/db/schema_arcs.sql`.

What happens
- On initialization the engine will call `services.arc_persistence.init_db(db_path)` and load existing arcs into memory.
- When choosing an action for a character, the engine calls `services.arc_weighting.weight_actions(actor_id, candidates, db_path)`.
- The weighting function returns deterministic weights derived from active arc goals. The engine selects the highest-weighted action (deterministic tie-breaker by action name).

Behavioral notes
- If `arc_weighting` or the DB is unavailable, the engine falls back to its in-memory selector (`_select_action_weighted`) which uses seeded randomness.
- The integration keeps the planner pure: `weight_actions` only returns enriched candidate weights and logs structured entries for diagnostics.

Tests
- See `tests/test_arc_weighting.py` and `tests/test_arc_persistence.py` for deterministic unit tests covering the weighting behavior.
