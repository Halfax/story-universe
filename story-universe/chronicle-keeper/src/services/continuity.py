
"""
Continuity Validator Logic for Chronicle Keeper
------------------------------------------------
This module provides the ContinuityValidator class, which checks incoming events for contradictions and ensures they fit the canonical world state.

Validation checks include:
- Contradictions with existing canon
- Valid character locations
- Timeline consistency
- Relationship preservation
- World rules enforcement
"""


class ContinuityValidator:
    def __init__(self, world_state):
        self.world_state = world_state

    def validate_event(self, event):
        """
        Expanded event validation:
        - Checks event type
        - Character existence and status (not dead/missing)
        - Location existence
        - Timestamp ordering (no past events)
        - Forbids contradictions (e.g., dead characters acting)
        Returns (bool, str): (is_valid, reason)
        """
        if not event.get("type"):
            return False, "Event type missing"

        char_id = event.get("character_id")
        if char_id:
            char = self.world_state.get("characters", {}).get(str(char_id))
            if not char:
                return False, f"Character {char_id} does not exist"
            if char.get("status") in ("dead", "missing"):
                return False, f"Character {char_id} is {char.get('status')}"

        loc_id = event.get("location_id")
        if loc_id:
            if loc_id not in self.world_state.get("locations", {}):
                return False, f"Location {loc_id} does not exist"

        # Timestamp ordering: event timestamp must be >= world time
        world_time = int(self.world_state.get("time", 0))
        if event.get("timestamp") is not None:
            try:
                if int(event["timestamp"]) < world_time:
                    return False, "Event timestamp is in the past"
            except Exception:
                return False, "Invalid event timestamp"

        # Example forbidden contradiction: dead character acting
        if event.get("type") == "action" and char_id:
            char = self.world_state.get("characters", {}).get(str(char_id))
            if char and char.get("status") == "dead":
                return False, f"Dead character {char_id} cannot act"

        # Faction relationship check (example: cannot attack ally)
        if event.get("type") == "faction_event":
            factions = self.world_state.get("factions", {})
            source_faction = event.get("source_faction_id")
            target_faction = event.get("target_faction_id")
            if source_faction and target_faction:
                rels = factions.get(str(source_faction), {}).get("relationships", {})
                if rels.get(str(target_faction)) == "ally" and event.get("action") == "attack":
                    return False, "Cannot attack an allied faction"

        # Duplicate event check (by id)
        if "id" in event:
            recent_events = self.world_state.get("recent_events", [])
            if any(e.get("id") == event["id"] for e in recent_events):
                return False, "Duplicate event detected"

        return True, "Valid"
