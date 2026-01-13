"""Minimal Narrative Engine

Provides a small, test-friendly `NarrativeEngine` with a `generate_event()`
method used by the test harness. This is intentionally lightweight: it can be
extended later into the full planner/selector/persona/arc layers described
in the roadmap.
"""
from __future__ import annotations

import time
import random
import uuid
from typing import Optional, Dict, Any, List
import os
import json
import logging

try:
    from services import arc_persistence
except Exception:
    arc_persistence = None
try:
    from services import arc_weighting
except Exception:
    arc_weighting = None


class NarrativeEngine:
    """Small narrative engine used for local development and tests.

    - `generate_event()` returns either `None` (no event this tick) or a
      simple event dictionary with `id`, `type`, `timestamp`, `source`, and
      `data`.
    - Maintains a tiny in-memory `arcs` store to demonstrate arc creation and
      basic progression.
    - Character AI is a simple chooser that uses seeded randomness and
      optional `character_traits` if provided via `seed_characters`.
    """

    def __init__(self, pi_base_url: Optional[str] = None, seed: Optional[int] = None, db_path: Optional[str] = None):
        self.pi_base_url = pi_base_url
        # If `seed` is provided we use a seeded RNG for deterministic tests.
        # If `seed` is None we use the system RNG at runtime (non-deterministic).
        self.seed = seed
        self.random = random.Random(seed) if seed is not None else None
        self.arcs: Dict[str, Dict[str, Any]] = {}
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.db_path = db_path
        # If a DB path is provided, initialize schema and load arcs
        if self.db_path and arc_persistence:
            try:
                arc_persistence.init_db(self.db_path)
                for a in arc_persistence.list_arcs(self.db_path):
                    self.arcs[a['id']] = {
                        'name': a['name'],
                        'participants': a.get('participants', []),
                        'state': a.get('state', 'planned'),
                        'events': a.get('events', []),
                        'data': a.get('data', {}),
                    }
            except Exception:
                # DB optional - ignore failures for tests that don't provide DB
                pass

    def seed_characters(self, characters: List[Dict[str, Any]]):
        """Load a small character set (id, name, traits) to drive AI choices."""
        for c in characters:
            cid = str(c.get("id") or uuid.uuid4())
            self.characters[cid] = {
                "name": c.get("name", "Anon"),
                "traits": c.get("traits", {}),
            }

    def create_arc(self, name: str, participants: List[str]) -> str:
        arc_id = str(uuid.uuid4())
        self.arcs[arc_id] = {"name": name, "participants": participants, "state": "planned", "events": []}
        if self.db_path and arc_persistence:
            try:
                arc_persistence.create_arc(self.db_path, {
                    'id': arc_id,
                    'name': name,
                    'state': 'planned',
                    'participants': participants,
                    'events': [],
                    'goals': [],
                    'data': {},
                })
            except Exception:
                pass
        return arc_id

    # Persistence
    def save_state(self, path: str) -> None:
        """Persist engine state (arcs and characters) to a JSON file."""
        import json

        data = {"arcs": self.arcs, "characters": self.characters}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        self._state_file = path

    def load_state(self, path: str) -> None:
        """Load engine state from a JSON file (if exists)."""
        import json, os

        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.arcs = data.get("arcs", {})
        self.characters = data.get("characters", {})
        self._state_file = path

    # Selector / Planner
    def _select_action_weighted(self, char_id: Optional[str]) -> str:
        """Select an action using a small planner: weight actions by arc urgency and traits."""
        base_actions = ["explore", "attack", "gather", "trade", "rest"]
        weights = {a: 1.0 for a in base_actions}

        # If character participates in an active arc, favor arc-related actions
        for aid, arc in self.arcs.items():
            if arc.get("state") == "active" and char_id and char_id in arc.get("participants", []):
                # increase weight for 'explore' or 'attack' depending on arc name heuristic
                if "war" in arc.get("name", "").lower() or "attack" in arc.get("name", "").lower():
                    weights["attack"] += 3.0
                else:
                    weights["explore"] += 2.0

        # Trait influence
        if char_id and char_id in self.characters:
            traits = self.characters[char_id].get("traits", {})
            if traits.get("aggressive", 0) > 0.6:
                weights["attack"] += 2.0
            if traits.get("curious", 0) > 0.5:
                weights["explore"] += 1.5

        # normalize to choices
        total = sum(weights.values())
        rng = self.random if self.random is not None else random
        if total <= 0:
            return rng.choice(base_actions)
        pick = rng.random() * total
        cum = 0.0
        for a in base_actions:
            cum += weights[a]
            if pick <= cum:
                return a
        return base_actions[-1]

    def advance_arc(self, arc_id: str, event: Dict[str, Any]) -> None:
        arc = self.arcs.get(arc_id)
        if not arc:
            return
        arc["events"].append(event)
        # simple state machine for demo
        if arc["state"] == "planned":
            arc["state"] = "active"
        elif arc["state"] == "active" and len(arc["events"]) > 3:
            arc["state"] = "resolved"
        # persist updates if DB is enabled
        if self.db_path and arc_persistence:
            try:
                arc_persistence.update_arc(self.db_path, arc_id, {
                    'state': arc['state'],
                    'events': arc['events'],
                    'participants': arc.get('participants', []),
                    'data': arc.get('data', {}),
                })
            except Exception:
                pass

    def _choose_character(self) -> Optional[str]:
        if not self.characters:
            return None
        rng = self.random if self.random is not None else random
        return rng.choice(list(self.characters.keys()))

    def _choose_action_for(self, char_id: Optional[str]) -> str:
        # If DB-backed weighting is available and a DB path was provided, use it
        base_actions = ["explore", "attack", "gather", "trade", "rest"]
        if self.db_path and arc_weighting:
            try:
                weighted = arc_weighting.weight_actions(char_id or "world", base_actions, self.db_path)
                if weighted:
                    # Use weighted sampling (deterministic with engine seed)
                    choices = [w["action"] for w in weighted]
                    weights = [w.get("normalized", 0.0) for w in weighted]
                    total = sum(weights)
                    if total <= 0:
                        # fallback deterministic pick
                        return choices[0]
                    rng = self.random if self.random is not None else random
                    r = rng.random() * total
                    cum = 0.0
                    for action, wt in zip(choices, weights):
                        cum += wt
                        if r <= cum:
                            chosen = action
                            # telemetry
                            try:
                                log = {
                                    "timestamp": int(time.time()),
                                    "actor": char_id or "world",
                                    "chosen_action": chosen,
                                    "candidates": weighted,
                                    "seeded": self.seed is not None,
                                    "method": "db_weighting",
                                }
                                logging.getLogger("narrative.telemetry").info(json.dumps(log))
                            except Exception:
                                pass
                            return chosen
                    # fallback last
                    chosen = choices[-1]
                    try:
                        log = {
                            "timestamp": int(time.time()),
                            "actor": char_id or "world",
                            "chosen_action": chosen,
                            "candidates": weighted,
                            "seeded": self.seed is not None,
                            "method": "db_weighting",
                        }
                        logging.getLogger("narrative.telemetry").info(json.dumps(log))
                    except Exception:
                        pass
                    return chosen
            except Exception:
                # fallback to local planner
                pass

        # Use planner/selector that weights actions by arc and traits
        chosen = self._select_action_weighted(char_id)
        # telemetry for in-memory selection
        try:
            log = {
                "timestamp": int(time.time()),
                "actor": char_id or "world",
                "chosen_action": chosen,
                "weights": {},
                "seeded": self.seed is not None,
                "method": "in_memory",
            }
            # include weights snapshot (best-effort)
            # reconstruct base weights for logging
            base_actions = ["explore", "attack", "gather", "trade", "rest"]
            weights = {a: 1.0 for a in base_actions}
            for aid, arc in self.arcs.items():
                if arc.get("state") == "active" and char_id and char_id in arc.get("participants", []):
                    if "war" in arc.get("name", "").lower() or "attack" in arc.get("name", "").lower():
                        weights["attack"] += 3.0
                    else:
                        weights["explore"] += 2.0
            if char_id and char_id in self.characters:
                traits = self.characters[char_id].get("traits", {})
                if traits.get("aggressive", 0) > 0.6:
                    weights["attack"] += 2.0
                if traits.get("curious", 0) > 0.5:
                    weights["explore"] += 1.5
            log["weights"] = weights
            logging.getLogger("narrative.telemetry").info(json.dumps(log))
        except Exception:
            pass
        return chosen

    def generate_event(self) -> Optional[Dict[str, Any]]:
        """Generate a single event or return None.

        Probability and content are intentionally simple to keep tests deterministic
        when a `seed` is provided.
        """
        # small chance to produce no event
        if self.random.random() < 0.2:
            return None

        char_id = self._choose_character()
        action = self._choose_action_for(char_id)
        ev = {
            "id": str(uuid.uuid4()),
            "type": "character.action" if char_id else "world.tick",
            "timestamp": int(time.time()),
            "source": "narrative-engine",
            "data": {
                "character_id": char_id,
                "action": action,
            },
            "metadata": {
                "correlationId": str(uuid.uuid4())
            }
        }

        # If this event fits an arc participant, advance an arc
        for aid, arc in list(self.arcs.items()):
            if char_id and char_id in arc.get("participants", []):
                self.advance_arc(aid, ev)
                break

        return ev

    def process_external_event(self, event: Dict[str, Any]) -> None:
        """Accept an externally-constructed event (e.g., from API) and
        optionally use it to start/advance arcs or influence character state.
        """
        # If event includes `start_arc` in metadata, create an arc
        meta = event.get("metadata") or {}
        if meta.get("start_arc"):
            name = meta.get("arc_name") or f"arc_{int(time.time())}"
            participants = meta.get("participants") or []
            self.create_arc(name, participants)

        # Apply simple influence: if event is aggressive, nudge participant trait
        if event.get("type") == "character.action" and event.get("data", {}).get("action") == "attack":
            cid = event.get("data", {}).get("character_id")
            if cid:
                c = self.characters.setdefault(cid, {"name": "Anon", "traits": {}})
                traits = c.setdefault("traits", {})
                traits["aggressive"] = min(1.0, float(traits.get("aggressive", 0.0)) + 0.02)


# Backwards compatible alias used by tests
DefaultNarrativeEngine = NarrativeEngine
