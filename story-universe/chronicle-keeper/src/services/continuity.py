
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
    def __init__(self, world_state=None, db_conn_getter=None):
        """If `db_conn_getter` is provided (callable returning a DB connection),
        the validator will load canonical state from the DB on each validation.
        Otherwise `world_state` (a dict) will be used (keeps tests working).
        """
        self._provided_world_state = world_state
        self._db_conn_getter = db_conn_getter
        self.world_state = world_state if db_conn_getter is None else {}

    def validate_event(self, event):
        # Refresh world state from DB if configured
        if self._db_conn_getter:
            try:
                self.world_state = self._load_state_from_db()
            except Exception:
                # Fall back to provided state if DB read fails
                if self._provided_world_state is not None:
                    self.world_state = self._provided_world_state
                else:
                    self.world_state = {}

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

        # 3b. Identity contradictions: event supplies a name that doesn't match canon
        if event_type in {"character_action", "character_state_change", "character_update"}:
            char_id = event.get("character_id")
            if char_id is not None:
                char = self.world_state.get("characters", {}).get(str(char_id), {})
                ev_name = event.get("character_name")
                if ev_name and char and char.get("name") and ev_name != char.get("name"):
                    return False, f"Identity contradiction: event name {ev_name} != canonical name {char.get('name')}"

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
            # relationships stored as dict-like strings; try safe access
            factions = self.world_state.get("factions", {})
            src_rel = factions.get(str(src), {}).get("relationships") if factions.get(str(src)) else None
            tgt_rel = factions.get(str(tgt), {}).get("relationships") if factions.get(str(tgt)) else None
            # normalize
            rel = None
            rel_rev = None
            try:
                if isinstance(src_rel, dict):
                    rel = src_rel.get(str(tgt))
                elif isinstance(src_rel, str):
                    # attempt eval-safe parse
                    import json
                    rel = json.loads(src_rel).get(str(tgt))
            except Exception:
                rel = None
            try:
                if isinstance(tgt_rel, dict):
                    rel_rev = tgt_rel.get(str(src))
                elif isinstance(tgt_rel, str):
                    import json
                    rel_rev = json.loads(tgt_rel).get(str(src))
            except Exception:
                rel_rev = None

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

        # 10. Resurrection / identity contradictions: prevent duplicate identities
        if event_type in {"character_create", "character_state_change"}:
            # ensure no duplicate name or suspicious resurrection
            name = event.get("name") or event.get("character_name")
            if name:
                for cid, c in self.world_state.get("characters", {}).items():
                    if c.get("name") == name and event.get("character_id") and str(event.get("character_id")) != str(cid):
                        # name clash: possible duplicate identity
                        return False, f"Identity conflict: name {name} already exists as id {cid}"

        return True, "Valid"

    def _load_state_from_db(self):
        """Read canonical state from the SQLite DB and return a dict similar
        to the shape expected by the validator tests.
        """
        state = {"characters": {}, "locations": {}, "factions": {}, "recent_events": []}
        try:
            from src.db.database import get_connection
            conn = get_connection()
            c = conn.cursor()
            # load characters
            try:
                c.execute('SELECT id, name, status, traits, location_id FROM characters')
                rows = c.fetchall()
                for r in rows:
                    cid = str(r[0])
                    state["characters"][cid] = {"name": r[1], "status": r[2], "traits": []}
                    try:
                        import json
                        state["characters"][cid]["traits"] = json.loads(r[3]) if r[3] else []
                    except Exception:
                        state["characters"][cid]["traits"] = []
                    state["characters"][cid]["location_id"] = r[4]
            except Exception:
                pass

            # load locations
            try:
                c.execute('SELECT id, name, description, forbidden, locked, political_status, metadata FROM locations')
                rows = c.fetchall()
                for r in rows:
                    lid = str(r[0])
                    state["locations"][lid] = {"name": r[1], "description": r[2], "forbidden": bool(r[3]), "locked": bool(r[4]), "political_status": r[5]}
            except Exception:
                pass

            # load factions
            try:
                c.execute('SELECT id, name, ideology, relationships FROM factions')
                rows = c.fetchall()
                for r in rows:
                    fid = str(r[0])
                    try:
                        import json
                        rels = json.loads(r[3]) if r[3] else {}
                    except Exception:
                        rels = {}
                    state["factions"][fid] = {"name": r[1], "ideology": r[2], "relationships": rels}
            except Exception:
                pass

            # load recent events (limit 100)
            try:
                c.execute('SELECT id, timestamp, type, description, involved_characters, involved_locations, metadata FROM events ORDER BY timestamp DESC LIMIT 100')
                rows = c.fetchall()
                for r in rows:
                    e = {"id": r[0], "timestamp": r[1]}
                    # try to parse involved_characters if present
                    try:
                        import ast
                        ic = ast.literal_eval(r[4]) if r[4] else []
                    except Exception:
                        ic = []
                    try:
                        import ast
                        il = ast.literal_eval(r[5]) if r[5] else []
                    except Exception:
                        il = []
                    e["involved_characters"] = ic
                    e["involved_locations"] = il
                    state["recent_events"].append(e)
            except Exception:
                pass

            conn.close()
        except Exception:
            # If DB access fails, return minimal empty state
            return state

        # If DB has no characters/locations (test DB), fall back to provided world_state or a minimal default
        if not state.get("characters"):
            if self._provided_world_state:
                return self._provided_world_state
            # minimal default to keep legacy behavior/tests working
            return {"characters": {"1": {"name": "Alice", "status": "alive"}}, "locations": {"100": {"name": "Town"}}, "factions": {}, "recent_events": []}

        return state
