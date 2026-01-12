Generator — Faction Integration

Summary
- The Narrative Engine now consults the Chronicle Keeper world state for `faction_metrics` and `faction_relationships` and uses these to bias event selection and faction choices.
- The generator biases toward `conflict` when average faction trust is low or many relationships have negative `strength` values, and toward `alliance` when average trust is high.
- When choosing factions for a `conflict`, the generator prefers explicit outgoing relationships with negative `strength` (hostility). For `alliance`, it prefers factions with higher `trust`.

Implementation notes
- The Chronicle Keeper `/world/state` endpoint was extended to include `faction_metrics`, `outgoing_relationships` and `cooldowns` so the generator has a single API to consult.
- The generator computes `avg_trust` and `avg_hostility` from the world state and adjusts the internal `tension` value used to weight event types.
- When selecting factions:
  - For `conflict`, the generator looks for explicit negative-strength pairs in `outgoing_relationships` and samples them preferentially.
  - For `alliance`, the generator sorts factions by `metrics.trust` and picks top candidates.

Tuning
- The weighting multipliers and thresholds are modest and can be tuned in `narrative-engine/src/event_generator.py`:
  - `tension` adjustment: `tension += (0.5 - avg_trust) * 0.5 + avg_hostility * 0.3`
  - Conflict boost uses `strength < 0` as hostility indicator.

Notes on robustness
- The generator falls back to previous behaviors if the Pi is unavailable or the augmented fields are missing.
- Faction `metrics` and `outgoing_relationships` are optional; the code defensively handles missing or malformed data.

Next steps
- Wire `personality_traits` into the generator as a per-faction bias (e.g., aggressive factions are sampled more often for conflict events).
- Add a small dashboard to visualize `trust` and `strength` histograms feeding the generator.
