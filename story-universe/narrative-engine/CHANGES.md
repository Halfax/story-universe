# Narrative Engine — Recent Changes

2026-01-12

- Seeded fallback characters and locations when the Chronicle Keeper returns no data. This prevents the generator from emitting empty, ungrounded narrative events (e.g., events with no involved characters or locations).
- Added pre-send validation in `NarrativeEngine.send_event()` to skip sending narrative events that lack participants (characters, factions, or locations). System events (types starting with `system`) are still sent.
- Added causation & correlation metadata to generated events (`metadata.causationId`, `metadata.correlationId`, and `source = "narrative_engine"`). This groups related events and links follow-ups to their triggers.

Why
- These changes reduce narrative noise when the Pi has no seeded world data, make generated events easier to trace, and give the Chronicle Keeper better signals for continuity validation.

Next recommended work
- Wire the Pi's `factions`/`characters` model into the engine so seeded data is unnecessary.
- Add more sophisticated planner integration to prefer goal-driven events over random sampling.
- Add an option to enable a mock-mode for local UI development (seed events and characters only for the World Browser).
