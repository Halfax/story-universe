# Event Parameterization Driven by Persona

This document explains how event parameters (severity, stability, aggressor/defender roles, arc assignment)
are derived from per-faction persona and metrics.

Rules implemented
- Conflict severity: weighted by aggressiveness of participants and inversely by mutual trust.
- Aggressor selection: the more aggressive faction is marked as aggressor.
- Alliance stability: weighted by diplomacy and mutual trust, reduced by paranoia.
- Arc assignment: if a dominant faction's persona for the event type exceeds 0.5, an arc of that type may start.

Files
- `narrative-engine/src/event_generator.py` — contains the sampling and parameterization logic.
- `narrative-engine/docs/FACTION_PERSONA_SAMPLING.md` — background on persona-driven sampling.

Tuning
- Adjust multipliers in `_conflict_weight`, `_alliance_weight`, and the parameter formulas above to change sensitivity.
