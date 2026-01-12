Personality Traits — Usage & Contract

Overview
- `factions.personality_traits` is a JSON/text blob stored on the `factions` table that encodes per-faction tendencies used by the validator and generator.
- Expected schema (flexible):
  - `aggressive` (0.0-1.0): higher values bias toward offensive actions and lower tolerance for diplomacy.
  - `diplomatic` (0.0-1.0): higher values bias toward alliances, reduce chance of initiating attacks.
  - `paranoid` (0.0-1.0): may increase defensive cooldowns or reduce trust thresholds.
  - `honorable` (0.0-1.0): reduces betrayal likelihood.

Validator behavior
- The `ContinuityValidator` now reads `personality_traits` from the world state and uses them to modulate decision thresholds:
  - High `aggressive` lowers the attack cutoff (allows attacks at lower `trust`).
  - High `diplomatic` raises alliance acceptance and increases attack cutoff.

Generator behavior
- The Narrative Engine uses `personality_traits` (when available) to bias faction selection — aggressive factions are sampled more for `conflict` events.
- If a faction has both `aggressive` and `diplomatic`, their numeric weights are combined to compute net bias.

Storage
- Store `personality_traits` as a JSON string in `factions.personality_traits` (e.g., `{"aggressive":0.7, "diplomatic":0.1}`).

Example
- A faction that is militaristic:
  - `personality_traits = {"aggressive": 0.9, "diplomatic": 0.05}`

- A faction focused on trade and alliances:
  - `personality_traits = {"aggressive": 0.05, "diplomatic": 0.85, "honorable":0.7}`

Notes
- Personality traits are advisory — they modulate validator thresholds and generator weightings but do not bypass hard constraints like explicit `ally` relationships or active cooldowns.
