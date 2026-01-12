# Faction Persona Sampling

This document describes how the Narrative Engine samples factions for multi-faction events
using their personality scores and metrics. The goal is to make per-faction identities
drive event selection so emergent behavior follows faction evolution.

Key points
- Per-faction persona keys: `aggressive`, `diplomatic`, `paranoia`, `curiosity`, `superstition` (0.0-1.0).
- The generator normalizes `personality_traits` from the Chronicle Keeper into `_persona_score`.
- For two-party events (`conflict`, `alliance`), the engine samples ordered pairs `(A,B)` using a
  weighted distribution computed from both factions' persona and metrics.

Weighting heuristics
- Conflict weight increases with:
  - faction aggression (both participants)
  - existing hostile relationship strength
  - lowered mutual trust
- Alliance weight increases with:
  - faction diplomacy (both participants)
  - mutual trust
  - decreased paranoia

Implementation notes
- See `narrative-engine/src/event_generator.py` for `_weighted_pair_sample`, `_conflict_weight`, and `_alliance_weight`.
- The sampling favors aggressive factions initiating conflicts even when global averages are peaceful,
  and lets diplomatic factions form alliances in otherwise tense contexts.

Tuning
- Adjust multipliers in `_conflict_weight` and `_alliance_weight` to control sensitivity.
