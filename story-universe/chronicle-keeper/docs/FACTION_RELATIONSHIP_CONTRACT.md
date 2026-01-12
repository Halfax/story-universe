**Faction Relationship Contract & Metrics**

Purpose
- Define canonical relationship types and numeric metrics used by the Chronicle Keeper to represent inter-faction state.

Canonical Relationship Types
- `ally` — strong positive relationship. Factions cooperate and avoid hostilities.
- `neutral` — default, no special affinity or hostility.
- `trade_partner` — primarily economic ties; may resist violent escalation.
- `vassal` — hierarchical relation where `source` is subordinate to `target`.
- `overlord` — hierarchical control where `source` holds authority over `target`.
- `rival` — competitive, may include sanctioned betrayals.
- `enemy` — hostile relation; escalations expected.
- `non_aggression` — formal pact preventing attacks for a duration.

Numeric Relationship Strength
- `strength` (float): range [-1.0, 1.0]. Negative values indicate hostility, positive values indicate friendliness.
- Typical mapping: `-1.0` (absolute enmity) ... `0` (neutral) ... `+1.0` (strong ally)

Metrics (per-faction)
- `trust` (float, 0.0-1.0): the baseline probability that other factions or the generator will consider cooperative actions valid. Default 0.5.
- `hostility` (derived): inverse of trust or computed from relationships/strengths.
- `influence` (int): abstract political weight used by generator heuristics.
- `power` (int): military/force capability.
- `resources` (int): economic capacity.

Cooldowns
- Relationship-level: each `faction_relationships` row includes `cooldown_until` (epoch seconds). While now < `cooldown_until`, certain aggressive actions are disallowed.
- Per-faction: `faction_cooldowns` stores arbitrary cooldown keys (e.g., `declare_war`, `form_alliance`) and `until_ts` timestamps.

Personality Traits
- Stored in `factions.personality_traits` as a JSON/text blob; expected to include boolean or numeric entries like `{ "aggressive": 0.7, "diplomatic": 0.2, "paranoid": 0.1 }`.
- Traits influence generator weighting and validator heuristics.

DB Artifacts
- `faction_relationships` table: source_faction_id, target_faction_id, relationship_type, strength, last_updated, cooldown_until, metadata
- `faction_cooldowns` table: faction_id, cooldown_key, until_ts, metadata
- `faction_metrics` table: per-faction metrics including `trust`, `power`, `resources`, `influence`
- `factions.personality_traits`: JSON/text field on the `factions` table

Validator Guidance
- Validators should consult `faction_metrics.trust` and `faction_relationships.strength` before accepting diplomatic or violent events.
- Low `trust` should prevent alliance formation; extreme hostility (`strength <= -0.9`) should disallow peaceful actions.
- Active cooldowns (relationship or faction-level) must block or delay prohibited actions.

API Endpoints (Chronicle Keeper)
- `GET /world/factions/{id}/relationships` — list outgoing relationships
- `PUT /world/factions/{id}/relationships/{target_id}` — upsert a relationship (admin)
- `GET /world/factions/{id}/cooldowns` — list cooldowns
- `PUT /world/factions/{id}/cooldowns/{key}` — set/update a cooldown (admin)

Examples
- Set a rivalry with strength -0.7:
  ```json
  PUT /world/factions/1/relationships/2
  { "relationship_type": "rival", "strength": -0.7 }
  ```

- Put a `declare_war` cooldown until epoch `1700000000`:
  ```json
  PUT /world/factions/1/cooldowns/declare_war
  { "until_ts": 1700000000 }
  ```

Notes
- Relationship types are intentionally extensible; use `metadata` for game-specific qualifiers.
- The generator and validator must agree on canonical types and numeric ranges; changes should be versioned.
