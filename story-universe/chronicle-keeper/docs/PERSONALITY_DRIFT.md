# Personality Drift

This document describes automatic personality drift for factions.

Principles
- Actions in the world cause small, persistent changes to faction personality traits.
- Drift is gradual (inertia) and guarded by a cooldown to avoid oscillation.
- Trait values are clamped to the range [0.0, 1.0].

Default tuning
- Per-action deltas (applied before inertia):
  - `attack` → `aggressive` +0.05
  - `form_alliance` → `diplomatic` +0.06
  - `betray` → `paranoia` +0.08
  - `explore` → `curiosity` +0.04
  - `mystery` → `superstition` +0.03
- Default inertia: 0.7 (higher = slower change)
- Persona cooldown: 3600 seconds (1 hour)

Implementation notes
- The validator's `apply_event_consequences` applies drift when handling `faction_event` events.
- Personality traits are stored on the `factions.personality_traits` JSON column.
- Cooldowns are recorded in `faction_cooldowns` under the `persona_drift` key.

Tuning
- To tune behavior, edit the module constants in `src/services/continuity.py`:
  - `PERSONA_DRIFT_DELTAS`
  - `PERSONA_INERTIA_DEFAULT`
  - `PERSONA_COOLDOWN_SECONDS`

Testing
- Unit tests should verify: idempotency during cooldown, accumulation across allowed windows, and clamping at [0.0,1.0].
