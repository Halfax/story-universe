
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
        # 1. Type check
        if "type" not in event:
            return False, "Event type missing"
        event_type = event["type"]

        # 2. Relationship constraints
        if event_type == "relationship_change":
            src = event.get("source_id")
            tgt = event.get("target_id")
            if src == tgt:
                return False, "Cannot set relationship to self"
            forbidden_types = {"archenemy"}
            if event.get("relationship_type") in forbidden_types:
                return False, "Relationship type forbidden"

        # 3. Character state transitions
        if event_type == "character_state_change":
            char_id = event.get("character_id")
            new_status = event.get("new_status")
            char = self.world_state.get("characters", {}).get(str(char_id), {})
            if char.get("status") == "dead" and new_status == "alive":
                return False, "Invalid character state transition: dead to alive"
            if char.get("status") == new_status:
                return False, "Invalid character state transition: already {}".format(new_status)
            if char.get("status") == "dead":
                return False, "Invalid character state transition: dead cannot change state"

        # 4. Dead character cannot act
        if event_type in {"action", "character_action"}:
            char_id = event.get("character_id")
            char = self.world_state.get("characters", {}).get(str(char_id), {})
            if char.get("status") == "dead":
                return False, "Character is dead and cannot act"

        # 5. Duplicate event
        if event.get("id") is not None:
            for e in self.world_state.get("recent_events", []):
                if e.get("id") == event["id"]:
                    return False, "Duplicate event ID"

        # 6. Faction rules
        if event_type == "faction_event":
            src = event.get("source_faction_id")
            tgt = event.get("target_faction_id")
            action = event.get("action")
            rel = self.world_state.get("factions", {}).get(str(src), {}).get("relationships", {}).get(str(tgt))
            rel_rev = self.world_state.get("factions", {}).get(str(tgt), {}).get("relationships", {}).get(str(src))
            if action == "attack" and rel == "ally":
                return False, "Cannot attack ally"
            if action == "form_alliance" and rel == "enemy":
                return False, "Cannot form alliance with enemy"
            if action == "betray" and (rel != "rival" and rel_rev != "rival"):
                return False, "Cannot betray without rivalry"

        # 7. Timeline consistency
        if event_type == "character_action" and event.get("timestamp") is not None:
            char_id = event.get("character_id")
            ts = event["timestamp"]
            for e in self.world_state.get("recent_events", []):
                if e.get("character_id") == char_id and e.get("timestamp", 0) > ts:
                    return False, "Timeline retroactive event for character"
            loc_id = event.get("location_id")
            if loc_id:
                for e in self.world_state.get("recent_events", []):
                    if e.get("location_id") == loc_id and e.get("timestamp", 0) > ts:
                        return False, "Timeline retroactive event for location"

        # 8. Location existence and constraints
        if event_type == "character_action" and event.get("location_id"):
            loc_id = event["location_id"]
            locations = self.world_state.get("locations", {})
            if loc_id not in locations:
                return False, f"Location {loc_id} does not exist"
            if locations[loc_id].get("forbidden"):
                return False, f"Location {loc_id} is forbidden"
            if locations[loc_id].get("locked"):
                return False, f"Location {loc_id} is locked"

        # 9. Lore-aware validation: magic, physics, politics
        if event_type == "character_action":
            char_id = event.get("character_id")
            char = self.world_state.get("characters", {}).get(str(char_id), {})
            # Magic: Only characters with 'magic' trait or permission can perform magic actions
            if event.get("action") == "cast_spell":
                if not char.get("traits") or "magic" not in char.get("traits", []):
                    return False, f"Lore: character {char_id} cannot cast spells (no magic trait)"
            # Physics: Forbid impossible actions (e.g., fly/teleport unless allowed)
            if event.get("action") in {"fly", "teleport"}:
                allowed = False
                if event.get("action") == "fly" and "fly" in char.get("traits", []):
                    allowed = True
                if event.get("action") == "teleport" and "teleport" in char.get("traits", []):
                    allowed = True
                if not allowed:
                    return False, f"Lore: character {char_id} cannot {event.get('action')} (forbidden by physics)"
            # Politics: Forbid entering forbidden regions or attacking protected characters
            if event.get("action") == "enter_region":
                loc_id = event.get("location_id")
                locations = self.world_state.get("locations", {})
                if loc_id in locations and locations[loc_id].get("political_status") == "forbidden":
                    return False, f"Lore: region {loc_id} is politically forbidden"
            if event.get("action") == "attack":
                target_id = event.get("target_id")
                chars = self.world_state.get("characters", {})
                if target_id in chars and chars[target_id].get("protected"):
                    return False, f"Lore: cannot attack protected character {target_id}"

        return True, "Valid"
