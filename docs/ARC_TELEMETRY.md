# Arc Sampling Telemetry

This document describes the structured telemetry emitted when the Narrative
Engine selects actions using either DB-backed weighting or the in-memory
fallback planner.

Fields emitted (JSON):
- `timestamp`: UNIX timestamp (int)
- `actor`: actor id or `world`
- `chosen_action`: the selected action string
- `method`: `db_weighting` or `in_memory`
- `seeded`: boolean — whether the engine was constructed with an explicit `seed`
- `candidates` (db_weighting only): array of candidate dicts returned by `arc_weighting.weight_actions` (includes `action`, `final_weight`, `normalized`, `logs`)
- `weights` (in_memory only): snapshot object mapping base action -> weight used by the in-memory planner

Logging location:
- Logged via Python `logging` to logger name `narrative.telemetry` at INFO level.

Usage:
- Configure your runtime to capture `narrative.telemetry` logs to a file or telemetry system.
- Use the `candidates` payload to analyze how arc goals shaped the distribution.
