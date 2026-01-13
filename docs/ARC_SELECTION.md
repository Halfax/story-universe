# Arc Selection (Probabilistic)

This document explains the weighted sampling selection used by the Narrative Engine when a DB-backed weighting is available.

Overview
- When `NarrativeEngine` is constructed with `db_path`, it will call `services.arc_weighting.weight_actions` to compute deterministic weights for candidate actions.
- The engine then uses its internal seeded RNG (`seed` parameter) to perform weighted sampling over the normalized weights. This keeps selection deterministic for tests when the same seed is used.

Runtime behavior
- If `seed` is not provided when constructing `NarrativeEngine`, the engine uses the system RNG for weighted sampling. This makes runtime selection stochastic so lower-weight actions can be chosen occasionally, enabling emergent behavior.
- To get deterministic behavior for tests, pass an explicit `seed` when constructing the engine.

Algorithm
- Let `weights` be the normalized weights returned by `weight_actions` (sum to 1).
- Draw `r = RNG.random() * sum(weights)` and select the first candidate where cumulative weight >= `r`.
- If weights sum to zero, the engine falls back to the first candidate deterministically.

Determinism & Testing
- Use the `seed` parameter when constructing `NarrativeEngine` to get reproducible behavior in unit tests (see `tests/test_arc_selection_sampling.py`).

Fallbacks
- If `arc_weighting` or the DB is unavailable, the engine falls back to the in-memory planner `_select_action_weighted`.
