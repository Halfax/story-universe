**Faction Names CSV**

- **File:** `chronicle-keeper/data/faction_names.csv`
- **Format:** CSV with header `category,name` where `category` is one of `fantasy_factions`, `fantasy_races`, `real_inspired`, `sci_fi`, or `uncategorized` and `name` is the faction name string.
- **Purpose:** Provides a large pool of human-readable faction names that can be used as fallback data by other services (eg. the Narrative Engine) when the Chronicle Keeper does not provide a live list of factions.

Integration
- The Narrative Engine (`narrative-engine/src/event_generator.py`) will attempt to fetch factions from the Chronicle Keeper API (`GET /world/factions`). If that call returns no factions, the engine falls back to sampling names from this CSV. Sampled faction names are included in generated events as the `involved_factions` field and appended to the `description` for readability.

Guidance
- To regenerate names, use the generator script: `chronicle-keeper/tools/faction_generator.py`.
- The CSV is intentionally large (tens of thousands of names) to support procedural generation; consumers should sample rather than load everything into memory if running in constrained environments.

Maintenance
- When adding or editing entries, preserve the `category,name` header and keep names unique; run the supplied dedupe utility or scripts in `tools/` to avoid duplicates.
