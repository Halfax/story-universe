# Arc-Goal Weighting

This document describes the deterministic, DB-backed weighting layer used by the planner.

Key points:

- Flow:
  1. Fetch active arcs relevant to the actor.
 2. Extract goals and compute progress (0–1).
 3. Map goal types to candidate actions using `GOAL_ACTION_MAP`.
 4. Apply weight delta = `priority * (1 - progress)` to matching candidates.
 5. Normalize resulting weights and return enriched candidates.

- Determinism: weights computed from DB fields (`target_value`, `current_value`, `priority`) and a static mapping.
- Logging: every contribution is logged as a structured JSON entry to help debug emergent decisions.
