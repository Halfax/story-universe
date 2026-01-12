Faction Validation Rules (Chronicle Keeper)

Overview
- These rules are enforced by `src/services/continuity.py` when validating incoming `faction_event` actions.

Key rules
- Alliance formation:
  - Requires the source faction `trust` metric to be >= `alliance_threshold` (default 0.2).
  - `personality_traits.diplomatic` lowers the threshold; `personality_traits.aggressive` raises it.
  - Per-faction cooldown `form_alliance` blocks alliance attempts while active.

- Attacks / aggressive actions:
  - Blocked against explicit allies or very positive relationship strength (>= 0.5).
  - If a relationship row has strongly negative `strength` (< -0.2) the validator permits aggressive actions even if the source faction's `trust` is low (hostile override).
  - Global per-faction cooldowns (e.g., `declare_war`) block actions while active.
  - Relationship-level `cooldown_until` blocks aggressive actions targeting that relationship while the cooldown is in effect.

- Betrayal:
  - The validator requires either an explicit `rival` relationship or a sufficiently negative numeric `strength` to allow `betray` actions; otherwise `betray` is rejected.

- General cooldown enforcement:
  - `faction_cooldowns` rows are checked by `cooldown_key` and will block matching actions while `until_ts` &gt; now.
  - Relationship rows (`faction_relationships`) include `cooldown_until` which blocks relationship-targeted actions while active.

Notes
- The validator attempts to read DB-backed state when a `db_conn_getter` is provided; tests may inject an in-memory DB with `faction_metrics`, `faction_relationships`, and `faction_cooldowns` rows to assert behavior.
- Tuning values (thresholds, hostile override margin) live in `src/services/continuity.py` and can be adjusted to change gating sensitivity.

Examples
- A faction with `trust=0.15` and `diplomatic=0.9` can still form an alliance because the diplomatic persona lowers the alliance threshold.
- Two factions with a relationship row of `strength = -0.7` are considered hostile; attack actions targeting that relationship bypass low-trust attack thresholds.
