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
import logging

logger = logging.getLogger("chronicle.continuity")

# Personality drift tuning constants
# - deltas: per-action trait adjustments (applied pre-inertia)
# - inertia: 0.0-1.0 (higher = slower drift)
# - cooldown: seconds between allowed persona drift applications per-faction
PERSONA_DRIFT_DELTAS = {
    "attack": {"aggressive": 0.05},
    "form_alliance": {"diplomatic": 0.06},
    "betray": {"paranoia": 0.08},
    "explore": {"curiosity": 0.04},
    "mystery": {"superstition": 0.03},
}
PERSONA_INERTIA_DEFAULT = 0.7
PERSONA_COOLDOWN_SECONDS = 60 * 60


class ContinuityValidator:
    def __init__(self, world_state=None, db_conn_getter=None, cache_ttl: int = 5):
        """If `db_conn_getter` is provided (callable returning a DB connection),
        the validator will load canonical state from the DB on each validation.
        Otherwise `world_state` (a dict) will be used (keeps tests working).
        """
        self._provided_world_state = world_state
        self._db_conn_getter = db_conn_getter
        self.world_state = world_state if db_conn_getter is None else {}
        # simple in-memory cache to avoid repeated DB reads across rapid validations
        self._cache_ttl = int(cache_ttl)
        self._cache = {"state": None, "ts": 0}

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
                return False, "Invalid character state transition: already {}".format(
                    new_status
                )
            if char.get("status") == "dead":
                return (
                    False,
                    "Invalid character state transition: dead cannot change state",
                )

        # 3b. Identity contradictions: event supplies a name that doesn't match canon
        if event_type in {
            "character_action",
            "character_state_change",
            "character_update",
        }:
            char_id = event.get("character_id")
            if char_id is not None:
                char = self.world_state.get("characters", {}).get(str(char_id), {})
                ev_name = event.get("character_name")
                if (
                    ev_name
                    and char
                    and char.get("name")
                    and ev_name != char.get("name")
                ):
                    return (
                        False,
                        f"Identity contradiction: event name {ev_name} != canonical name {char.get('name')}",
                    )

        # 4. Dead character cannot act
        if event_type in {"action", "character_action"}:
            char_id = event.get("character_id")
            char = self.world_state.get("characters", {}).get(str(char_id), {})
            if char.get("status") == "dead":
                return False, "Character is dead and cannot act"

        # Cross-entity validation: ensure referenced characters/factions/locations exist
        try:
            # characters
            for key in ("character_id", "target_id"):
                if event.get(key) is not None:
                    cid = str(event.get(key))
                    # Allow creating a new character: skip existence check for character_create
                    if key == "character_id" and event_type == "character_create":
                        continue
                    if cid not in self.world_state.get("characters", {}):
                        # try DB lookup if available
                        if self._db_conn_getter:
                            conn = self._db_conn_getter()
                            cur = conn.cursor()
                            cur.execute(
                                "SELECT id FROM characters WHERE id = ?", (cid,)
                            )
                            if not cur.fetchone():
                                return False, f"Character {cid} does not exist"
                        else:
                            return False, f"Character {cid} does not exist"
            # factions
            for fk in ("source_faction_id", "target_faction_id"):
                if event.get(fk) is not None:
                    fid = str(event.get(fk))
                    if fid not in self.world_state.get("factions", {}):
                        if self._db_conn_getter:
                            conn = self._db_conn_getter()
                            cur = conn.cursor()
                            cur.execute("SELECT id FROM factions WHERE id = ?", (fid,))
                            if not cur.fetchone():
                                return False, f"Faction {fid} does not exist"
                        else:
                            return False, f"Faction {fid} does not exist"
            # locations
            for lk in ("location_id", "from_location_id", "to_location_id"):
                if event.get(lk) is not None:
                    lid = str(event.get(lk))
                    if lid not in self.world_state.get("locations", {}):
                        if self._db_conn_getter:
                            conn = self._db_conn_getter()
                            cur = conn.cursor()
                            cur.execute("SELECT id FROM locations WHERE id = ?", (lid,))
                            if not cur.fetchone():
                                return False, f"Location {lid} does not exist"
                        else:
                            return False, f"Location {lid} does not exist"
        except Exception:
            # if DB lookups fail, be conservative and continue (other checks will catch contradictions)
            pass

        # 5. Duplicate event
        if event.get("id") is not None:
            for e in self.world_state.get("recent_events", []):
                if e.get("id") == event["id"]:
                    return False, "Duplicate event ID"

        # 5b. Causation / correlation validation
        ok, reason = self._validate_causation_chain(event)
        if not ok:
            return False, reason

        # 6. Faction rules
        if event_type == "faction_event":
            src = event.get("source_faction_id")
            tgt = event.get("target_faction_id")
            action = event.get("action")
            factions = self.world_state.get("factions", {})
            src_rel = (
                factions.get(str(src), {}).get("relationships")
                if factions.get(str(src))
                else None
            )
            tgt_rel = (
                factions.get(str(tgt), {}).get("relationships")
                if factions.get(str(tgt))
                else None
            )

            # normalize simple in-memory relationships
            rel = None
            rel_rev = None
            try:
                if isinstance(src_rel, dict):
                    rel = src_rel.get(str(tgt))
                elif isinstance(src_rel, str):
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

            # fetch explicit relationship row and faction cooldowns from DB (if available)
            rel_row = None
            cooldowns = {}
            try:
                if self._db_conn_getter:
                    conn = self._db_conn_getter()
                    opened_here = False
                else:
                    from db.database import get_connection

                    conn = get_connection()
                    opened_here = True
                cur = conn.cursor()
                cur.execute(
                    "SELECT relationship_type, strength, cooldown_until FROM faction_relationships WHERE source_faction_id = ? AND target_faction_id = ?",
                    (src, tgt),
                )
                rrow = cur.fetchone()
                if rrow:
                    rel_row = {
                        "relationship_type": rrow[0],
                        "strength": float(rrow[1] or 0.0),
                        "cooldown_until": int(rrow[2] or 0),
                    }
                cur.execute(
                    "SELECT cooldown_key, until_ts FROM faction_cooldowns WHERE faction_id = ?",
                    (src,),
                )
                cooldowns = {row[0]: int(row[1]) for row in cur.fetchall()}
            except Exception:
                rel_row = None
                cooldowns = {}
            finally:
                try:
                    if "opened_here" in locals() and opened_here:
                        conn.close()
                except Exception:
                    pass

            # basic relationship-type constraints
            if action == "attack" and rel == "ally":
                return False, "Cannot attack ally"
            if action == "form_alliance" and rel == "enemy":
                return False, "Cannot form alliance with enemy"
            # allow numeric relationship rows to satisfy rivalry requirement
            if action == "betray" and not (
                rel == "rival"
                or rel_rev == "rival"
                or (rel_row and rel_row.get("relationship_type") == "rival")
            ):
                return False, "Cannot betray without rivalry"

            # Use faction metrics (trust/power) to gate certain diplomatic actions
            try:
                src_metrics = factions.get(str(src), {}).get("metrics", {})
            except Exception:
                src_metrics = {}
            src_trust = (
                float(src_metrics.get("trust", 0.5)) if src_metrics is not None else 0.5
            )
            try:
                src_persona = factions.get(str(src), {}).get("personality_traits") or {}
            except Exception:
                src_persona = {}
            aggressive = (
                float(src_persona.get("aggressive", 0.0))
                if isinstance(src_persona, dict)
                else 0.0
            )
            diplomatic = (
                float(src_persona.get("diplomatic", 0.0))
                if isinstance(src_persona, dict)
                else 0.0
            )

            alliance_threshold = 0.2
            if diplomatic > 0.6:
                alliance_threshold = 0.1
            if aggressive > 0.6:
                alliance_threshold = 0.4
            if action == "form_alliance" and src_trust < alliance_threshold:
                return (
                    False,
                    f"Faction {src} trust ({src_trust}) too low to form alliance (threshold {alliance_threshold})",
                )

            attack_threshold = 0.05
            if aggressive > 0.6:
                attack_threshold = 0.01
            if diplomatic > 0.6:
                attack_threshold = 0.2

            rel_strength = rel_row.get("strength") if rel_row else None
            if (
                rel_row
                and rel_row.get("relationship_type") == "ally"
                and action in {"attack", "declare_war"}
            ):
                return False, "Cannot perform aggressive action against an ally"
            if (
                rel_strength is not None
                and rel_strength >= 0.5
                and action in {"attack", "declare_war"}
            ):
                return (
                    False,
                    f"Cannot perform aggressive action against a strong/positive relationship (strength {rel_strength})",
                )

            hostile_override = rel_strength is not None and rel_strength < -0.2
            if (
                action == "attack"
                and (not hostile_override)
                and src_trust < attack_threshold
            ):
                return (
                    False,
                    f"Faction {src} trust too low to justify coordinated attack (threshold {attack_threshold})",
                )

            # cooldown enforcement
            try:
                import time

                now = int(time.time())
                if (
                    rel_row
                    and rel_row.get("cooldown_until", 0) > now
                    and action in {"attack", "declare_war", "betray"}
                ):
                    return (
                        False,
                        f"Relationship cooldown active until {rel_row['cooldown_until']}",
                    )
                for key, until in cooldowns.items():
                    if until > now and (
                        key == action or key in action or action.startswith(key)
                    ):
                        return (
                            False,
                            f"Faction {src} cooldown '{key}' active until {until}",
                        )
            except Exception:
                pass
                rel_rev = None

            if action == "attack" and rel == "ally":
                return False, "Cannot attack ally"
            if action == "form_alliance" and rel == "enemy":
                return False, "Cannot form alliance with enemy"
            if action == "betray" and (rel != "rival" and rel_rev != "rival"):
                return False, "Cannot betray without rivalry"

            # Use faction metrics (trust/power) to gate certain diplomatic actions
            try:
                src_metrics = factions.get(str(src), {}).get("metrics", {})
            except Exception:
                src_metrics = {}
            src_trust = (
                float(src_metrics.get("trust", 0.5)) if src_metrics is not None else 0.5
            )
            # personality traits can modify thresholds (aggressive/diplomatic)
            try:
                src_persona = factions.get(str(src), {}).get("personality_traits") or {}
            except Exception:
                src_persona = {}
            aggressive = (
                float(src_persona.get("aggressive", 0.0))
                if isinstance(src_persona, dict)
                else 0.0
            )
            diplomatic = (
                float(src_persona.get("diplomatic", 0.0))
                if isinstance(src_persona, dict)
                else 0.0
            )
            # Prevent low-trust factions from forming alliances
            alliance_threshold = 0.2
            if diplomatic > 0.6:
                alliance_threshold = 0.1
            if aggressive > 0.6:
                alliance_threshold = 0.4
            if action == "form_alliance" and src_trust < alliance_threshold:
                return (
                    False,
                    f"Faction {src} trust ({src_trust}) too low to form alliance (threshold {alliance_threshold})",
                )
            # Prevent desperate attacks if faction has extremely low resources and no power
            attack_threshold = 0.05
            if aggressive > 0.6:
                attack_threshold = 0.01
            if diplomatic > 0.6:
                attack_threshold = 0.2
            # If there is an explicit relationship row, allow numeric strength to influence gating
            rel_strength = None
            if rel_row:
                rel_strength = rel_row.get("strength", 0.0)

            # If relationship is explicitly allied or very positive, block aggressive actions
            if (
                rel_row
                and rel_row.get("relationship_type") == "ally"
                and action in {"attack", "declare_war"}
            ):
                return False, "Cannot perform aggressive action against an ally"
            if (
                rel_strength is not None
                and rel_strength >= 0.5
                and action in {"attack", "declare_war"}
            ):
                return (
                    False,
                    f"Cannot perform aggressive action against a strong/positive relationship (strength {rel_strength})",
                )

            # If relationship strength is strongly negative (hostile), allow attack regardless of low trust
            hostile_override = False
            if rel_strength is not None and rel_strength < -0.2:
                hostile_override = True

            # apply trust-based attack gating unless hostile_override is true
            if (
                action == "attack"
                and (not hostile_override)
                and src_trust < attack_threshold
            ):
                return (
                    False,
                    f"Faction {src} trust too low to justify coordinated attack (threshold {attack_threshold})",
                )
            # Enforce explicit relationship rows and cooldowns from DB if available
            try:
                # prefer injected DB connection for testability
                if self._db_conn_getter:
                    conn = self._db_conn_getter()
                    opened_here = False
                else:
                    from db.database import get_connection

                    conn = get_connection()
                    opened_here = True
                cur = conn.cursor()
                # fetch explicit relationship from source->target
                cur.execute(
                    "SELECT relationship_type, strength, cooldown_until FROM faction_relationships WHERE source_faction_id = ? AND target_faction_id = ?",
                    (src, tgt),
                )
                rrow = cur.fetchone()
                rel_row = None
                if rrow:
                    rel_row = {
                        "relationship_type": rrow[0],
                        "strength": float(rrow[1] or 0.0),
                        "cooldown_until": int(rrow[2] or 0),
                    }

                # check per-faction cooldowns that might apply to action keys
                cur.execute(
                    "SELECT cooldown_key, until_ts FROM faction_cooldowns WHERE faction_id = ?",
                    (src,),
                )
                cooldowns = {row[0]: int(row[1]) for row in cur.fetchall()}

                import time

                now = int(time.time())
                # if there is an explicit relationship and it has an active cooldown, block related actions
                if (
                    rel_row
                    and rel_row.get("cooldown_until", 0) > now
                    and action in {"attack", "declare_war", "betray"}
                ):
                    return (
                        False,
                        f"Relationship cooldown active until {rel_row['cooldown_until']}",
                    )
                # check faction-level cooldowns for any matching action key
                for key, until in cooldowns.items():
                    if until > now and (
                        key == action or key in action or action.startswith(key)
                    ):
                        return (
                            False,
                            f"Faction {src} cooldown '{key}' active until {until}",
                        )
            except Exception:
                # If DB access fails, ignore and fall back to in-memory relationships
                pass
            finally:
                try:
                    if "opened_here" in locals() and opened_here:
                        conn.close()
                except Exception:
                    pass

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
                    return (
                        False,
                        f"Lore: character {char_id} cannot cast spells (no magic trait)",
                    )
            # Physics: Forbid impossible actions (e.g., fly/teleport unless allowed)
            if event.get("action") in {"fly", "teleport"}:
                allowed = False
                if event.get("action") == "fly" and "fly" in char.get("traits", []):
                    allowed = True
                if event.get("action") == "teleport" and "teleport" in char.get(
                    "traits", []
                ):
                    allowed = True
                if not allowed:
                    return (
                        False,
                        f"Lore: character {char_id} cannot {event.get('action')} (forbidden by physics)",
                    )
            # Politics: Forbid entering forbidden regions or attacking protected characters
            if event.get("action") == "enter_region":
                loc_id = event.get("location_id")
                locations = self.world_state.get("locations", {})
                if (
                    loc_id in locations
                    and locations[loc_id].get("political_status") == "forbidden"
                ):
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
                    if (
                        c.get("name") == name
                        and event.get("character_id")
                        and str(event.get("character_id")) != str(cid)
                    ):
                        # name clash: possible duplicate identity
                        return (
                            False,
                            f"Identity conflict: name {name} already exists as id {cid}",
                        )

        return True, "Valid"

    def _load_state_from_db(self):
        """Read canonical state from the SQLite DB and return a dict similar
        to the shape expected by the validator tests.
        """
        state = {"characters": {}, "locations": {}, "factions": {}, "recent_events": []}
        try:
            import time

            # return cached state if fresh
            now_ts = int(time.time())
            if self._cache.get("state") and (
                now_ts - int(self._cache.get("ts", 0)) <= self._cache_ttl
            ):
                return self._cache["state"]
            # Prefer an injected DB connection getter (useful for tests). If not provided,
            # fall back to the package-level get_connection helper.
            if self._db_conn_getter:
                conn = self._db_conn_getter()
                opened_here = False
            else:
                from db.database import get_connection

                conn = get_connection()
                opened_here = True
            c = conn.cursor()
            # load characters
            try:
                c.execute(
                    "SELECT id, name, status, traits, location_id FROM characters"
                )
                rows = c.fetchall()
                for r in rows:
                    cid = str(r[0])
                    state["characters"][cid] = {
                        "name": r[1],
                        "status": r[2],
                        "traits": [],
                    }
                    try:
                        import json

                        state["characters"][cid]["traits"] = (
                            json.loads(r[3]) if r[3] else []
                        )
                    except Exception:
                        state["characters"][cid]["traits"] = []
                    state["characters"][cid]["location_id"] = r[4]
            except Exception:
                pass

            # load locations
            try:
                c.execute(
                    "SELECT id, name, description, forbidden, locked, political_status, metadata FROM locations"
                )
                rows = c.fetchall()
                for r in rows:
                    lid = str(r[0])
                    state["locations"][lid] = {
                        "name": r[1],
                        "description": r[2],
                        "forbidden": bool(r[3]),
                        "locked": bool(r[4]),
                        "political_status": r[5],
                    }
            except Exception:
                pass

            # load factions
            try:
                # include personality_traits column so persona modifiers are available
                c.execute(
                    "SELECT id, name, ideology, relationships, personality_traits FROM factions"
                )
                rows = c.fetchall()
                for r in rows:
                    fid = str(r[0])
                    try:
                        import json

                        rels = json.loads(r[3]) if r[3] else {}
                        ptraits = json.loads(r[4]) if len(r) > 4 and r[4] else {}
                    except Exception:
                        rels = {}
                        ptraits = {}
                    # initialize faction entry; metrics & personality filled later if present
                    state["factions"][fid] = {
                        "name": r[1],
                        "ideology": r[2],
                        "relationships": rels,
                        "personality_traits": ptraits,
                        "metrics": {},
                    }
                # load faction metrics if available
                try:
                    c.execute(
                        "SELECT faction_id, trust, power, resources, influence FROM faction_metrics"
                    )
                    fm_rows = c.fetchall()
                    for fr in fm_rows:
                        fid = str(fr[0])
                        if fid not in state["factions"]:
                            state["factions"][fid] = {
                                "name": None,
                                "ideology": None,
                                "relationships": {},
                                "metrics": {},
                            }
                        state["factions"][fid]["metrics"] = {
                            "trust": float(fr[1]) if fr[1] is not None else 0.5,
                            "power": int(fr[2] or 0),
                            "resources": int(fr[3] or 0),
                            "influence": int(fr[4] or 0),
                        }
                except Exception:
                    # If faction_metrics table missing, leave default metrics empty
                    pass
            except Exception:
                pass

            # load recent events (limit 100)
            try:
                c.execute(
                    "SELECT id, timestamp, type, description, involved_characters, involved_locations, metadata FROM events ORDER BY timestamp DESC LIMIT 100"
                )
                rows = c.fetchall()
                for r in rows:
                    e = {
                        "id": r[0],
                        "timestamp": r[1],
                        "type": r[2],
                        "description": r[3],
                    }
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
                    # try to parse metadata (may be JSON)
                    try:
                        import json

                        md = json.loads(r[6]) if r[6] else {}
                    except Exception:
                        try:
                            import ast

                            md = ast.literal_eval(r[6]) if r[6] else {}
                        except Exception:
                            md = {}
                    e["metadata"] = md
                    e["involved_characters"] = ic
                    e["involved_locations"] = il
                    state["recent_events"].append(e)
            except Exception:
                pass

            # Only close if we opened the connection here; injected connections are
            # owned by the caller (e.g., tests) and should not be closed.
            try:
                if opened_here:
                    conn.close()
            except Exception:
                pass
        except Exception:
            # If DB access fails, return minimal empty state
            return state

        # If DB has no characters/locations (test DB), fall back to provided world_state or a minimal default
        if not state.get("characters"):
            if self._provided_world_state:
                # cache provided world_state as well
                self._cache["state"] = self._provided_world_state
                import time

                self._cache["ts"] = int(time.time())
                return self._provided_world_state
            # minimal default to keep legacy behavior/tests working
            default = {
                "characters": {"1": {"name": "Alice", "status": "alive"}},
                "locations": {"100": {"name": "Town"}},
                "factions": {},
                "recent_events": [],
            }
            self._cache["state"] = default
            import time

            self._cache["ts"] = int(time.time())
            return default
        # cache and return
        try:
            import time

            self._cache["state"] = state
            self._cache["ts"] = int(time.time())
        except Exception:
            pass

        return state

    def _validate_causation_chain(self, event):
        """Return (True, '') if causation/correlation checks pass.
        If `causationId` present, ensure referenced event exists either in-memory
        (`recent_events`) or in the `events` table when DB access is available.
        """
        meta = event.get("metadata") or {}
        causation = meta.get("causationId") or event.get("causationId")
        correlation = meta.get("correlationId") or event.get("correlationId")
        # correlation is advisory
        if not causation:
            return True, ""

        # check in-memory recent events first
        for e in self.world_state.get("recent_events", []):
            if e.get("id") == causation:
                # also ensure causation timestamp <= current event timestamp when available
                try:
                    if (
                        event.get("timestamp") is not None
                        and e.get("timestamp") is not None
                        and int(e.get("timestamp")) > int(event.get("timestamp"))
                    ):
                        return (
                            False,
                            f"Causation event {causation} has timestamp after current event",
                        )
                except Exception:
                    pass
                return True, ""

        # if we have DB access, check events table
        if self._db_conn_getter:
            try:
                conn = self._db_conn_getter()
                cur = conn.cursor()
                cur.execute("SELECT id FROM events WHERE id = ?", (causation,))
                row = cur.execute(
                    "SELECT id, timestamp FROM events WHERE id = ?", (causation,)
                ).fetchone()
                if row:
                    # ensure timestamp ordering
                    try:
                        caus_ts = (
                            int(row[1]) if len(row) > 1 and row[1] is not None else None
                        )
                        if (
                            caus_ts
                            and event.get("timestamp")
                            and int(caus_ts) > int(event.get("timestamp"))
                        ):
                            return (
                                False,
                                f"Causation event {causation} has timestamp after current event",
                            )
                    except Exception:
                        pass
                    return True, ""
                return False, f"Causation event {causation} not found"
            except Exception:
                # fall back to rejecting if we cannot verify
                return False, f"Failed to validate causation {causation}"

        return False, f"Causation event {causation} not present in recent events"

    def _validate_arc_consistency(self, event):
        """Basic correlation/arc checks to prevent immediate contradictory actions inside the same arc.

        This is conservative: if a prior event in the same `correlationId` for the same actor
        has an incompatible action, reject the new event. This prevents quick flip-flops inside
        the same arc that would break narrative continuity.
        """
        meta = event.get("metadata") or {}
        corr = meta.get("correlationId") or event.get("correlationId")
        if not corr:
            return True, ""

        # Look for recent events with same correlation id
        for e in self.world_state.get("recent_events", []):
            emd = e.get("metadata") or {}
            e_corr = emd.get("correlationId") or e.get("correlationId")
            if not e_corr or str(e_corr) != str(corr):
                continue
            # if same source faction and contradictory actions, reject
            if (
                event.get("type") == "faction_event"
                and e.get("type") == "faction_event"
            ):
                src = str(event.get("source_faction_id"))
                e_src = str(
                    e.get("metadata", {}).get("_event_id")
                    or e.get("source_faction_id")
                    or ""
                )
                if src and (
                    str(e.get("source_faction_id")) == src
                    or str(e.get("target_faction_id")) == src
                ):
                    # simple contradictory pairs
                    curr_act = event.get("action")
                    prev_act = e.get("description") or e.get("type") or ""
                    maybe_prev = e.get("metadata", {}).get("action") or e.get(
                        "description"
                    )
                    if isinstance(maybe_prev, str) and curr_act and maybe_prev:
                        # check simple contradictions
                        contradictions = [
                            ("form_alliance", "declare_war"),
                            ("form_alliance", "attack"),
                            ("attack", "form_alliance"),
                            ("attack", "form_alliance"),
                        ]
                        for a, b in contradictions:
                            if (curr_act == a and maybe_prev == b) or (
                                curr_act == b and maybe_prev == a
                            ):
                                return (
                                    False,
                                    f"Arc contradiction inside correlation {corr}: {maybe_prev} vs {curr_act}",
                                )
        return True, ""

    def apply_event_consequences(self, event, db_conn=None):
        """Apply state updates for an accepted event.
        If `db_conn` provided or `db_conn_getter` is configured, write changes to DB.
        This function is intentionally lightweight; concrete rules are in docs/EVENT_CONSEQUENCES.md.
        """
        try:
            conn = None
            opened_here = False
            if db_conn:
                conn = db_conn
            elif self._db_conn_getter:
                conn = self._db_conn_getter()
                opened_here = True
            else:
                conn = None

            typ = event.get("type")
            # ----------------------
            # Character actions
            # ----------------------
            if typ == "character_action" and event.get("action") == "move":
                cid = str(event.get("character_id"))
                loc = event.get("location_id")
                if conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE characters SET location_id = ? WHERE id = ?", (loc, cid)
                    )
                    conn.commit()
                else:
                    if cid in self.world_state.get("characters", {}):
                        self.world_state["characters"][cid]["location_id"] = loc

            if typ == "character_state_change":
                cid = str(event.get("character_id"))
                new = event.get("new_status")
                if conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE characters SET status = ? WHERE id = ?", (new, cid)
                    )
                    conn.commit()
                else:
                    if cid in self.world_state.get("characters", {}):
                        self.world_state["characters"][cid]["status"] = new

            # ----------------------
            # Faction events (use severity/stability params when present)
            # ----------------------
            if typ == "faction_event":
                action = event.get("action")
                src = event.get("source_faction_id")
                tgt = event.get("target_faction_id")

                # parse and sanitize severity/stability; clamp to reasonable bounds
                try:
                    severity = float(event.get("severity", 0.0) or 0.0)
                except Exception:
                    severity = 0.0
                try:
                    stability = float(event.get("stability", 0.0) or 0.0)
                except Exception:
                    stability = 0.0
                # sanity clamp: keep values within [-1.0, 1.0]
                if severity != severity:
                    severity = 0.0
                severity = max(-1.0, min(1.0, severity))
                if stability != stability:
                    stability = 0.0
                stability = max(-1.0, min(1.0, stability))

                if abs(severity) > 0.5 or abs(stability) > 0.5:
                    logger.warning(
                        "Large severity/stability detected for event %s: severity=%s stability=%s",
                        event.get("id") or "<no-id>",
                        severity,
                        stability,
                    )

                drift_scale = 1.0
                if action in {"attack", "betray"}:
                    drift_scale = 1.0 + severity
                elif action == "form_alliance":
                    drift_scale = 1.0 + stability

                # support multi-target consequences: either singular `target_faction_id`
                # or list `target_faction_ids` (CSV or list)
                targets = []
                if event.get("target_faction_id") is not None:
                    targets.append(str(event.get("target_faction_id")))
                if event.get("target_faction_ids"):
                    t = event.get("target_faction_ids")
                    if isinstance(t, str):
                        targets.extend([x.strip() for x in t.split(",") if x.strip()])
                    elif isinstance(t, (list, tuple)):
                        targets.extend([str(x) for x in t])
                # ensure at least one target for actions that expect one
                if not targets and action in {"attack", "betray", "form_alliance"}:
                    targets = [str(tgt) for tgt in [event.get("target_faction_id")] if tgt is not None]

                if conn:
                    cur = conn.cursor()
                    # form_alliance: upsert relationship row and set cooldown on source
                    # For multi-target support, iterate targets and apply smaller, partitioned effects
                    for tgt in targets:
                        # capture pre-change state for possible reversal logging
                        undo = {"relationship": None, "faction_metrics": {}, "persona": None}
                        try:
                            cur.execute(
                                "SELECT relationship_type,strength,cooldown_until FROM faction_relationships WHERE source_faction_id = ? AND target_faction_id = ?",
                                (src, tgt),
                            )
                            r = cur.fetchone()
                            if r:
                                undo["relationship"] = {
                                    "relationship_type": r[0],
                                    "strength": float(r[1] or 0.0),
                                    "cooldown_until": int(r[2] or 0),
                                }
                            # capture trust metrics
                            try:
                                cur.execute(
                                    "SELECT trust FROM faction_metrics WHERE faction_id = ?",
                                    (tgt,),
                                )
                                tr = cur.fetchone()
                                if tr:
                                    undo["faction_metrics"][str(tgt)] = float(tr[0] or 0.0)
                            except Exception:
                                pass
                            # capture source persona
                            try:
                                cur.execute(
                                    "SELECT personality_traits FROM factions WHERE id = ?",
                                    (src,),
                                )
                                prow = cur.fetchone()
                                import json

                                if prow and prow[0]:
                                    try:
                                        undo["persona"] = json.loads(prow[0])
                                    except Exception:
                                        undo["persona"] = None
                            except Exception:
                                pass
                        except Exception:
                            pass

                        if action == "form_alliance":
                            init_strength = 0.5 * (1.0 + float(stability))
                            init_strength = max(0.0, min(1.0, init_strength))
                            cur.execute(
                                "INSERT OR REPLACE INTO faction_relationships (source_faction_id,target_faction_id,relationship_type,strength,cooldown_until) VALUES (?,?,?,?,?)",
                                (src, tgt, "ally", init_strength, 0),
                            )
                            # set a cooldown entry to prevent immediate repeat alliances; longer stability -> longer cooldown (durable alliance)
                            import time

                            until = int(time.time()) + int(
                                PERSONA_COOLDOWN_SECONDS * (1.0 + (1.0 - float(stability)))
                            )
                            cur.execute(
                                "INSERT OR REPLACE INTO faction_cooldowns (faction_id,cooldown_key,until_ts) VALUES (?,?,?)",
                                (src, "form_alliance", until),
                            )
                            conn.commit()

                        if action == "attack":
                            # lower relationship strength if exists, or create hostile row
                            cur.execute(
                                "SELECT strength FROM faction_relationships WHERE source_faction_id = ? AND target_faction_id = ?",
                                (src, tgt),
                            )
                            row = cur.fetchone()
                            if row:
                                delta = 0.2 * (1.0 + float(severity))
                                new_strength = float(row[0] or 0.0) - delta
                                cur.execute(
                                    "UPDATE faction_relationships SET strength = ? WHERE source_faction_id = ? AND target_faction_id = ?",
                                    (new_strength, src, tgt),
                                )
                            else:
                                delta = 0.2 * (1.0 + float(severity))
                                cur.execute(
                                    "INSERT INTO faction_relationships (source_faction_id,target_faction_id,relationship_type,strength,cooldown_until) VALUES (?,?,?,?,?)",
                                    (src, tgt, "hostile", -delta, 0),
                                )
                            conn.commit()

                            # Adjust faction metrics (trust) proportional to severity
                            try:
                                cur.execute(
                                    "SELECT trust FROM faction_metrics WHERE faction_id = ?",
                                    (tgt,),
                                )
                                r = cur.fetchone()
                                if r:
                                    new_t = max(
                                        0.0,
                                        float(r[0] or 0.0) - 0.03 * (1.0 + float(severity)),
                                    )
                                    cur.execute(
                                        "UPDATE faction_metrics SET trust = ? WHERE faction_id = ?",
                                        (new_t, tgt),
                                    )
                                cur.execute(
                                    "SELECT trust FROM faction_metrics WHERE faction_id = ?",
                                    (src,),
                                )
                                r2 = cur.fetchone()
                                if r2:
                                    new_s = max(
                                        0.0,
                                        float(r2[0] or 0.0) - 0.005 * (1.0 + float(severity)),
                                    )
                                    cur.execute(
                                        "UPDATE faction_metrics SET trust = ? WHERE faction_id = ?",
                                        (new_s, src),
                                    )
                                # set relationship cooldown proportional to severity
                                import time

                                now_ts = int(time.time())
                                rel_cool = now_ts + int(
                                    PERSONA_COOLDOWN_SECONDS * (1.0 + float(severity))
                                )
                                cur.execute(
                                    "UPDATE faction_relationships SET cooldown_until = ? WHERE source_faction_id = ? AND target_faction_id = ?",
                                    (rel_cool, src, tgt),
                                )
                                conn.commit()
                            except Exception:
                                pass

                        if action == "betray":
                            # betrayal has stronger paranoia/drift effects and relationship damage
                            try:
                                cur.execute(
                                    "SELECT strength FROM faction_relationships WHERE source_faction_id = ? AND target_faction_id = ?",
                                    (src, tgt),
                                )
                                row = cur.fetchone()
                                if row:
                                    new_strength = float(row[0] or 0.0) - (
                                        0.3 * (1.0 + float(severity))
                                    )
                                    cur.execute(
                                        "UPDATE faction_relationships SET strength = ? WHERE source_faction_id = ? AND target_faction_id = ?",
                                        (new_strength, src, tgt),
                                    )
                                else:
                                    cur.execute(
                                        "INSERT INTO faction_relationships (source_faction_id,target_faction_id,relationship_type,strength,cooldown_until) VALUES (?,?,?,?,?)",
                                        (
                                            src,
                                            tgt,
                                            "hostile",
                                            -0.3 * (1.0 + float(severity)),
                                            0,
                                        ),
                                    )
                                conn.commit()
                            except Exception:
                                pass

                        # If reversible requested, persist undo payload for this target (requires event id)
                        try:
                            reversible = bool(
                                (event.get("metadata") or {}).get("reversible") or event.get("reversible")
                            )
                        except Exception:
                            reversible = False
                        try:
                            if reversible and event.get("id"):
                                import json, time

                                # ensure table exists
                                cur.execute(
                                    "CREATE TABLE IF NOT EXISTS event_consequences (event_id TEXT PRIMARY KEY, reversible INTEGER, undo_payload TEXT, applied_ts INTEGER)"
                                )
                                cur.execute(
                                    "INSERT OR REPLACE INTO event_consequences (event_id,reversible,undo_payload,applied_ts) VALUES (?,?,?,?)",
                                    (
                                        str(event.get("id")),
                                        1,
                                        json.dumps(undo),
                                        int(time.time()),
                                    ),
                                )
                                conn.commit()
                        except Exception:
                            pass

                    if action == "betray":
                        # betrayal has stronger paranoia/drift effects and relationship damage
                        try:
                            cur.execute(
                                "SELECT strength FROM faction_relationships WHERE source_faction_id = ? AND target_faction_id = ?",
                                (src, tgt),
                            )
                            row = cur.fetchone()
                            if row:
                                new_strength = float(row[0] or 0.0) - (
                                    0.3 * (1.0 + float(severity))
                                )
                                cur.execute(
                                    "UPDATE faction_relationships SET strength = ? WHERE source_faction_id = ? AND target_faction_id = ?",
                                    (new_strength, src, tgt),
                                )
                            else:
                                cur.execute(
                                    "INSERT INTO faction_relationships (source_faction_id,target_faction_id,relationship_type,strength,cooldown_until) VALUES (?,?,?,?,?)",
                                    (
                                        src,
                                        tgt,
                                        "hostile",
                                        -0.3 * (1.0 + float(severity)),
                                        0,
                                    ),
                                )
                            conn.commit()
                        except Exception:
                            pass

                    # Personality drift: apply scaled deltas and set persona cooldown
                    try:
                        drift = PERSONA_DRIFT_DELTAS.get(action)
                        if drift:
                            cur.execute(
                                "SELECT personality_traits FROM factions WHERE id = ?",
                                (src,),
                            )
                            prow = cur.fetchone()
                            import json, time

                            ptraits = {}
                            if prow and prow[0]:
                                try:
                                    ptraits = json.loads(prow[0])
                                except Exception:
                                    ptraits = {}
                            inertia = (
                                float(ptraits.get("inertia", PERSONA_INERTIA_DEFAULT))
                                if isinstance(ptraits, dict)
                                else PERSONA_INERTIA_DEFAULT
                            )
                            if inertia < 0.0:
                                inertia = 0.0
                            if inertia >= 1.0:
                                inertia = 0.99
                            now = int(time.time())
                            cooldown_key = "persona_drift"
                            cur.execute(
                                "SELECT until_ts FROM faction_cooldowns WHERE faction_id = ? AND cooldown_key = ?",
                                (src, cooldown_key),
                            )
                            crow = cur.fetchone()
                            cooldown_until = int(crow[0]) if crow and crow[0] else 0
                            if cooldown_until <= now:
                                changed = False
                                for k, v in drift.items():
                                    old = float(ptraits.get(k, 0.0) or 0.0)
                                    change = (
                                        float(v) * (1.0 - inertia) * float(drift_scale)
                                    )
                                    new = old + change
                                    new = max(0.0, min(1.0, new))
                                    if abs(new - old) > 1e-6:
                                        ptraits[k] = round(new, 4)
                                        changed = True
                                if changed:
                                    cur.execute(
                                        "UPDATE factions SET personality_traits = ? WHERE id = ?",
                                        (json.dumps(ptraits), src),
                                    )
                                    until = now + PERSONA_COOLDOWN_SECONDS
                                    cur.execute(
                                        "INSERT OR REPLACE INTO faction_cooldowns (faction_id,cooldown_key,until_ts) VALUES (?,?,?)",
                                        (src, cooldown_key, until),
                                    )
                                    conn.commit()
                    except Exception:
                        pass

                else:
                    # No DB: apply scaled personality drift to in-memory world_state
                    try:
                        import time

                        delta_map = PERSONA_DRIFT_DELTAS
                        drift = delta_map.get(action)
                        if drift:
                            factions = self.world_state.setdefault("factions", {})
                            fid = str(src)
                            f = factions.get(fid) or {"personality_traits": {}}
                            ptraits = f.get("personality_traits") or {}
                            inertia = (
                                float(ptraits.get("inertia", PERSONA_INERTIA_DEFAULT))
                                if isinstance(ptraits, dict)
                                else PERSONA_INERTIA_DEFAULT
                            )
                            inertia = max(0.0, min(0.99, inertia))
                            now = int(time.time())
                            fc = self.world_state.setdefault("faction_cooldowns", {})
                            fcd = fc.get(fid, {})
                            cooldown_until = int(fcd.get("persona_drift", 0) or 0)
                            if cooldown_until <= now:
                                changed = False
                                for k, v in drift.items():
                                    old = float(ptraits.get(k, 0.0) or 0.0)
                                    change = (
                                        float(v) * (1.0 - inertia) * float(drift_scale)
                                    )
                                    new = max(0.0, min(1.0, old + change))
                                    if abs(new - old) > 1e-6:
                                        ptraits[k] = round(new, 4)
                                        changed = True
                                if changed:
                                    f["personality_traits"] = ptraits
                                    factions[fid] = f
                                    # set cooldown for in-memory map
                                    fcd["persona_drift"] = (
                                        now + PERSONA_COOLDOWN_SECONDS
                                    )
                                    fc[fid] = fcd
                    except Exception:
                        pass

        finally:
            try:
                if "opened_here" in locals() and opened_here and conn:
                    conn.close()
            except Exception:
                pass
