"""DB-backed arc-goal weighting for the planner.

Provides `weight_actions(actor_id, candidates, db_path)` which returns a list
of candidates with deterministic weights based on active arcs and their goals.

The module is intentionally small and testable. It reads arcs from the
`arcs` table (JSON columns) and applies the GOAL_ACTION_MAP weight rules.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Tuple

from .arc_persistence import list_arcs

logger = logging.getLogger(__name__)


# Static mapping from goal types to candidate action types
GOAL_ACTION_MAP: Dict[str, List[str]] = {
    "expand_influence": ["diplomacy", "propaganda", "alliance"],
    "weaken_rival": ["sabotage", "espionage", "military_pressure"],
    "secure_resource": ["trade", "explore", "resource_capture"],
    "restoration": ["repair", "stabilize", "rebuild"],
    "exploration": ["explore", "survey", "scout"],
}


def _compute_progress(goal: Dict[str, Any]) -> float:
    # Expect goal to have target_value and current_value
    target = float(goal.get("target_value", 1.0))
    current = float(goal.get("current_value", 0.0))
    if target <= 0:
        return 0.0
    delta = max(0.0, min(target, target - current))
    progress = 1.0 - (delta / target)
    # clamp
    return max(0.0, min(1.0, progress))


def _normalize_weights(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    total = sum(it.get("final_weight", 0.0) for it in items)
    if total <= 0:
        # assign uniform probability
        n = len(items)
        for it in items:
            it["normalized"] = 1.0 / n if n > 0 else 0.0
        return items
    for it in items:
        it["normalized"] = it.get("final_weight", 0.0) / total
    return items


def weight_actions(actor_id: str, candidates: List[Any], db_path: str) -> List[Dict[str, Any]]:
    """Weight candidate actions for `actor_id` using DB arc goals.

    - `candidates` may be a list of action strings or dicts with an `action` key.
    - Returns a list of dicts: `{action, base_weight, final_weight, normalized, logs}`.
    """
    # Normalize candidate shape
    normalized_candidates: List[Dict[str, Any]] = []
    for c in candidates:
        if isinstance(c, str):
            normalized_candidates.append({"action": c, "base_weight": 1.0, "final_weight": 1.0, "logs": []})
        elif isinstance(c, dict):
            action = c.get("action") or c.get("type")
            base = float(c.get("base_weight", 1.0))
            normalized_candidates.append({"action": action, "base_weight": base, "final_weight": base, "logs": []})
        else:
            raise ValueError("candidate must be str or dict with 'action'")

    # Fetch active arcs and filter for participation
    active_arcs = [a for a in list_arcs(db_path) if a.get("state") == "active"]
    relevant_arcs = []
    for a in active_arcs:
        participants = a.get("participants") or []
        if actor_id in participants:
            relevant_arcs.append(a)

    # For each relevant arc, process goals
    for arc in relevant_arcs:
        arc_id = arc.get("id")
        goals = arc.get("goals") or []
        for goal in goals:
            g_type = goal.get("type")
            priority = float(goal.get("priority", 1.0))
            progress = _compute_progress(goal)
            delta_weight_factor = (1.0 - progress)  # per plan

            mapped_actions = GOAL_ACTION_MAP.get(g_type, [])
            for cand in normalized_candidates:
                if cand["action"] in mapped_actions:
                    delta = priority * delta_weight_factor
                    prev = cand.get("final_weight", 0.0)
                    cand["final_weight"] = prev + delta
                    entry = {
                        "actor": actor_id,
                        "action": cand["action"],
                        "base_weight": cand["base_weight"],
                        "arc_id": arc_id,
                        "goal_type": g_type,
                        "goal_progress": progress,
                        "priority": priority,
                        "delta_weight": delta,
                        "final_weight": cand["final_weight"],
                    }
                    cand.setdefault("logs", []).append(entry)
                    logger.info(json.dumps(entry))

    # Normalize final weights
    _normalize_weights(normalized_candidates)
    # Add top-level log summary per candidate
    for cand in normalized_candidates:
        cand_summary = {
            "actor": actor_id,
            "action": cand["action"],
            "final_weight": cand["final_weight"],
            "normalized": cand.get("normalized"),
        }
        logger.info(json.dumps(cand_summary))

    return normalized_candidates
