"""Event generator for the Narrative Engine.

Implements lightweight logic for:
- querying the Chronicle Keeper (Pi) for world state, characters, factions, locations
- weighting event types by simple narrative needs
- tracking active story arcs and advancing them
- cooldowns to avoid spamming the same event types
- basic cause-and-effect followups

This is a scaffold intended for iterative improvement.
"""
from typing import Any, Dict, List, Optional
import time
import random
import requests
import json
import os
import csv
from pathlib import Path
try:
    from generators.character_gen import CharacterManager
except Exception:
    try:
        from src.generators.character_gen import CharacterManager
    except Exception:
        CharacterManager = None
try:
    from generators.narrative_planner import NarrativePlanner
except Exception:
    try:
        from src.generators.narrative_planner import NarrativePlanner
    except Exception:
        NarrativePlanner = None

try:
    from generators.embeddings import embed, similarity
except Exception:
    try:
        from src.generators.embeddings import embed, similarity
    except Exception:
        def embed(x):
            return []
        def similarity(a, b):
            return 0.0


STATE_FILE = os.path.join(os.path.dirname(__file__), "engine_state.json")


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"cooldowns": {}, "arcs": [], "last_event": None}
    return {"cooldowns": {}, "arcs": [], "last_event": None}


def save_state(state: Dict[str, Any]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


class NarrativeEngine:
    def __init__(self, pi_base_url: str = "http://localhost:8001") -> None:
        self.pi = pi_base_url.rstrip("/")
        self.state = load_state()
        # cooldowns: event_type -> unix timestamp when next allowed
        self.cooldowns: Dict[str, float] = self.state.get("cooldowns", {})
        # active arcs: list of {id, arc, characters, progress}
        self.arcs: List[Dict[str, Any]] = self.state.get("arcs", [])
        self.last_event: Optional[Dict[str, Any]] = self.state.get("last_event")
        # per-character goals: {char_id: {goal, progress, assigned_at}}
        self.char_goals: Dict[str, Dict[str, Any]] = self.state.get("char_goals", {})
        # per-character cooldowns to avoid reusing same characters each tick
        self.char_cooldowns: Dict[str, float] = self.state.get("char_cooldowns", {})
        # CharacterManager for richer character queries if available
        if CharacterManager:
            try:
                self.character_manager = CharacterManager(self.pi)
                self.character_manager.fetch_characters()
            except Exception:
                self.character_manager = None
        else:
            self.character_manager = None
        # Narrative planner
        if NarrativePlanner and self.character_manager:
            try:
                self.planner = NarrativePlanner(self.character_manager)
            except Exception:
                self.planner = None
        else:
            self.planner = None
        # local faction name lookup (fallback when Pi has no factions)
        self.local_factions = self._load_local_faction_names()

    # ----------------------
    # Pi queries
    # ----------------------
    def fetch_world_state(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.pi}/world/state", timeout=5)
            if r.ok:
                return r.json()
        except Exception:
            pass
        return {}

    def fetch_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.pi}/world/events/recent?limit={limit}", timeout=5)
            if r.ok:
                return r.json().get("events", [])
        except Exception:
            pass
        return []

    def fetch_characters(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.pi}/world/characters", timeout=5)
            if r.ok:
                return r.json().get("characters", [])
        except Exception:
            pass
        return []

    def fetch_locations(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.pi}/world/locations", timeout=5)
            if r.ok:
                return r.json().get("locations", [])
        except Exception:
            pass
        return []

    def fetch_factions(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.pi}/world/factions", timeout=5)
            if r.ok:
                return r.json().get("factions", [])
        except Exception:
            pass
        return []

    def _load_local_faction_names(self) -> Dict[str, List[str]]:
        """Load `chronicle-keeper/data/faction_names.csv` as a category->names map.

        Returns an empty dict if the file isn't available.
        """
        try:
            base = Path(__file__).resolve().parents[2]
            csv_path = base / 'chronicle-keeper' / 'data' / 'faction_names.csv'
            out: Dict[str, List[str]] = {}
            if not csv_path.exists():
                return out
            with csv_path.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cat = (row.get('category') or 'uncategorized').strip()
                    name = (row.get('name') or '').strip()
                    if not name:
                        continue
                    out.setdefault(cat, []).append(name)
            return out
        except Exception:
            return {}

    # ----------------------
    # Event generation helpers
    # ----------------------
    def _allowed_by_cooldown(self, event_type: str) -> bool:
        now = time.time()
        next_allowed = self.cooldowns.get(event_type, 0)
        return now >= next_allowed

    def _set_cooldown(self, event_type: str, seconds: int = 30) -> None:
        self.cooldowns[event_type] = time.time() + seconds

    def _set_char_cooldown(self, char_id: str, seconds: int = 60) -> None:
        self.char_cooldowns[str(char_id)] = time.time() + seconds

    def _allowed_character(self, char_id: str) -> bool:
        next_allowed = self.char_cooldowns.get(str(char_id), 0)
        return time.time() >= next_allowed

    def _choose_event_type(self, world_state: Dict[str, Any]) -> str:
        """Choose an event type weighted by simple narrative need.

        Uses a 'tension' value from world_state if present; falls back to random.
        Lower tension favors exploration/starting arcs, higher favors conflict/escalation.
        """
        tension = 0.5
        try:
            tension = float(world_state.get("tension", tension))
        except Exception:
            pass

        # base pool with weights
        pool = [
            ("explore", max(1, int((1 - tension) * 10))),
            ("conflict", max(1, int(tension * 10))),
            ("alliance", max(1, int((1 - tension) * 5))),
            ("mystery", 3),
            ("movement", 5),
            ("relationship", 4),
        ]

        # bias toward advancing active arcs: if there are arcs in-progress, boost their types
        arc_boosts: Dict[str, int] = {}
        for a in self.arcs:
            atype = a.get("arc")
            # older arcs (higher progress) should be more likely to get resolved
            prog = a.get("progress", 0)
            arc_boosts[atype] = arc_boosts.get(atype, 0) + max(1, 3 - prog)
        if arc_boosts:
            pool = [(t, w + arc_boosts.get(t, 0)) for (t, w) in pool]

        # if planner suggests an arc, bias toward that arc type
        if self.planner:
            try:
                plan = self.planner.generate_plan()
                if plan and plan.get("arc"):
                    arc = plan["arc"]
                    # map planner arc to event types where possible
                    mapping = {"quest": "explore", "conflict": "conflict", "alliance": "alliance", "mystery": "mystery"}
                    preferred = mapping.get(arc)
                    if preferred:
                        # boost preferred weight
                        pool = [(t, (w + 5) if t == preferred else w) for (t, w) in pool]
                        # start storing the planner arc in active arcs
                        chars = plan.get("characters") or []
                        if chars:
                            self._start_new_arc(preferred, chars)
            except Exception:
                pass

        # filter by cooldown
        filtered = [(t, w) for (t, w) in pool if self._allowed_by_cooldown(t)]
        if not filtered:
            # if all cooled down, ignore cooldowns for choice but still set one after
            filtered = pool

        types, weights = zip(*filtered)
        choice = random.choices(types, weights=weights, k=1)[0]
        return choice

    def _select_characters_for_event(self, characters: List[Dict[str, Any]], n: int = 1) -> List[str]:
        if not characters:
            return []
        # filter out dead characters or invalid entries
        characters = [c for c in characters if c and str(c.get('status','')).lower() != 'dead']
        if not characters:
            return []
        n = min(n, len(characters))
        # Prefer characters with goals that match a likely event type
        # Build a flat list of ids
        ids = [c.get("id") or c.get("character_id") or c.get("name") for c in characters]
        # ensure goals exist for characters
        self._ensure_goals_for_characters(characters)

        # filter out characters currently on cooldown
        characters = [c for c in characters if self._allowed_character(c.get('id') or c.get('character_id') or c.get('name'))]
        if not characters:
            return []

        # score characters by how active their goal is (lower progress preferred)
        scored = []
        for c in characters:
            cid = c.get("id") or c.get("character_id") or c.get("name")
            g = self.char_goals.get(str(cid))
            score = 1.0
            if g:
                # prefer characters with lower progress (more to do)
                score = max(0.1, 1.0 - (g.get("progress", 0) * 0.2))
            # small boost if character's goal matches likely event types inferred from world
            # e.g., if goal maps to 'explore' and tension is low, favor them
            goal = g.get("goal") if g else None
            if goal:
                if goal in ("explore", "undertake_quest", "discover_mystery"):
                    score *= 1.15
                if goal in ("seek_revenge", "gain_power"):
                    score *= 1.1
            scored.append((cid, score))

        # weighted sample by score
        total = sum(s for _, s in scored)
        if total <= 0:
            sampled_ids = random.sample(ids, n)
        else:
            weights = [s / total for _, s in scored]
            choices = [cid for cid, _ in scored]
            sampled_ids = random.choices(choices, weights=weights, k=n)

        # set per-character cooldown to avoid immediate reuse
        for cid in set(sampled_ids):
            self._set_char_cooldown(cid, seconds=30 + random.randint(0,30))

        return sampled_ids

    # ----------------------
    # Character goals
    # ----------------------
    def _infer_goal_from_traits(self, character: Dict[str, Any]) -> Optional[str]:
        traits = character.get("traits") or {}
        # traits may be dict or list
        trait_keys = []
        if isinstance(traits, dict):
            trait_keys = list(traits.keys())
        elif isinstance(traits, list):
            for t in traits:
                if isinstance(t, dict):
                    trait_keys.append(t.get("name") or t.get("trait"))
                else:
                    trait_keys.append(str(t))

        mapping = {
            "curious": "explore",
            "ambitious": "gain_power",
            "vengeful": "seek_revenge",
            "greedy": "acquire_wealth",
            "lonely": "seek_relationship",
            "brave": "undertake_quest",
            "scholar": "discover_mystery",
        }
        for k in trait_keys:
            if not k:
                continue
            lk = str(k).lower()
            if lk in mapping:
                return mapping[lk]
        return None

    def _ensure_goals_for_characters(self, characters: List[Dict[str, Any]]) -> None:
        for c in characters:
            cid = str(c.get("id") or c.get("character_id") or c.get("name"))
            if cid in self.char_goals:
                continue
            # explicit goals on character
            explicit = c.get("goals") or c.get("goal")
            if explicit:
                goal = explicit if isinstance(explicit, str) else (explicit[0] if isinstance(explicit, list) else None)
            else:
                goal = self._infer_goal_from_traits(c)

            if goal:
                self.char_goals[cid] = {"goal": goal, "progress": 0, "assigned_at": int(time.time())}

    def _progress_goal_for_characters(self, involved: List[str]) -> None:
        for cid in involved:
            g = self.char_goals.get(str(cid))
            if g:
                g["progress"] = g.get("progress", 0) + 1
                # resolve simple goals at progress>=3
                if g["progress"] >= 3:
                    # mark as completed by deleting
                    del self.char_goals[str(cid)]

    # ----------------------
    # Arc management
    # ----------------------
    def _start_new_arc(self, arc_type: str, characters: List[str]) -> Dict[str, Any]:
        arc = {"id": f"arc_{int(time.time())}_{random.randint(0,9999)}", "arc": arc_type, "characters": characters, "progress": 0, "created_at": int(time.time())}
        self.arcs.append(arc)
        return arc

    def _advance_arcs(self) -> None:
        for arc in self.arcs:
            arc["progress"] += 1
        # prune finished arcs (example threshold)
        self.arcs = [a for a in self.arcs if a.get("progress", 0) < 5]

    # ----------------------
    # Cause & Effect: simple follow-ups
    # ----------------------
    def _maybe_create_followup(self, last_event: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not last_event:
            return None
        # 30% chance to create a follow-up related to last event
        if random.random() > 0.3:
            return None
        # create a lightweight follow-up that escalates or resolves
        et = last_event.get("type", "event")
        if et == "conflict":
            ftype = random.choice(["conflict", "resolution"])
        else:
            ftype = random.choice(["mystery", "movement", "relationship"])

        # if last event had characters, continue with them
        chars = last_event.get("involved_characters") or []
        return {"type": ftype, "involved_characters": chars, "description": f"Follow-up to {last_event.get('id','?')}"}

    # ----------------------
    # Main generation
    # ----------------------
    def generate_event(self) -> Optional[Dict[str, Any]]:
        world = self.fetch_world_state()
        characters = self.fetch_characters()
        locations = self.fetch_locations()
        factions = self.fetch_factions()

        # Planner-first: if planner suggests a concrete event, prefer it (if not cooled down)
        if self.planner:
            try:
                plan = self.planner.generate_plan()
                if plan and isinstance(plan, dict) and plan.get('event'):
                    suggested = plan.get('event')
                    etype = suggested.get('type')
                    if etype and self._allowed_by_cooldown(etype):
                        # adopt planner event
                        suggested['id'] = f"evt_{int(time.time())}_{random.randint(0,9999)}"
                        suggested['timestamp'] = int(time.time())
                        self._set_cooldown(etype, seconds=30)
                        self.last_event = suggested
                        # persist state
                        self.state.update({"cooldowns": self.cooldowns, "arcs": self.arcs, "last_event": self.last_event})
                        save_state(self.state)
                        return suggested
            except Exception:
                pass

        # try a cause-effect followup first
        follow = self._maybe_create_followup(self.last_event)
        if follow:
            etype = follow["type"]
            if not self._allowed_by_cooldown(etype):
                follow = None
            else:
                self._set_cooldown(etype, seconds=20)

        if follow:
            event = follow
        else:
            etype = self._choose_event_type(world)
            # pick number of characters based on event type
            if etype in ("conflict", "alliance"):
                n = 2
            elif etype == "movement":
                n = 1
            else:
                n = 1

            involved = self._select_characters_for_event(characters, n)

            # use location/faction data if available
            loc = None
            if locations:
                loc = random.choice(locations).get("id")

            # determine factions: prefer Pi-provided factions, else sample from local list
            involved_factions: List[str] = []
            if factions:
                # Pi returns list of faction dicts; extract ids or names
                names = [f.get("name") or f.get("id") for f in factions]
                names = [x for x in names if x]
                if names:
                    # choose 1-2 factions depending on event type
                    k = 2 if etype in ("conflict", "alliance") else 1
                    involved_factions = random.sample(names, min(k, len(names)))
            else:
                # fallback to local CSV
                # sample by category relevant to the event
                cat_choice = 'fantasy_factions'
                if etype == 'alliance' or etype == 'conflict':
                    cat_choice = random.choice(['fantasy_factions', 'real_inspired', 'sci_fi'])
                elif etype == 'movement':
                    cat_choice = 'real_inspired'
                elif etype == 'explore':
                    cat_choice = 'fantasy_factions'

                pool = self.local_factions.get(cat_choice) or []
                if pool:
                    k = 2 if etype in ("conflict", "alliance") else 1
                    involved_factions = random.sample(pool, min(k, len(pool)))

            desc = f"{etype} involving {', '.join(map(str, involved))}"
            if involved_factions:
                desc += f"; factions: {', '.join(involved_factions)}"

            event = {
                "type": etype,
                "involved_characters": involved,
                "involved_locations": [loc] if loc else [],
                "involved_factions": involved_factions,
                "description": desc,
            }

            # start or advance arcs for certain event types
            if etype in ("explore", "conflict", "mystery") and involved:
                # 50% chance to join an existing arc involving these characters
                joined = False
                for arc in self.arcs:
                    if set(arc.get("characters", [])) & set(involved):
                        arc["progress"] += 1
                        joined = True
                        break
                if not joined and random.random() < 0.4:
                    self._start_new_arc(etype, involved)

            # set cooldown for the chosen type
            self._set_cooldown(etype, seconds=30 + random.randint(0,30))

        # update last_event and save state
        event_id = f"evt_{int(time.time())}_{random.randint(0,9999)}"
        event["id"] = event_id
        event["timestamp"] = int(time.time())

        self.last_event = event
        self.state.update({"cooldowns": self.cooldowns, "arcs": self.arcs, "last_event": self.last_event})
        save_state(self.state)

        return event

    # ----------------------
    # Send to Pi
    # ----------------------
    def send_event(self, event: Dict[str, Any]) -> bool:
        try:
            r = requests.post(f"{self.pi}/event", json=event, timeout=5)
            return r.ok
        except Exception:
            return False


if __name__ == "__main__":
    # simple CLI to generate one event and post it
    eng = NarrativeEngine("http://localhost:8001")
    ev = eng.generate_event()
    if ev:
        print("Generated event:", json.dumps(ev, indent=2))
        ok = eng.send_event(ev)
        print("Sent to Pi:", ok)

