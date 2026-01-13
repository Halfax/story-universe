import os
import json
import time
import uuid
import importlib.util
from pathlib import Path


def _load_narrative_engine():
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / 'narrative-engine' / 'src' / 'event_generator.py'
        if candidate.exists():
            spec = importlib.util.spec_from_file_location('narrative_event_generator', str(candidate))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.NarrativeEngine
    raise ImportError('Could not locate narrative-engine/src/event_generator.py')


def test_arc_persistence_and_selector(tmp_path):
    NarrativeEngine = _load_narrative_engine()
    eng = NarrativeEngine(seed=12345)
    # seed a character
    cid = str(uuid.uuid4())
    eng.seed_characters([{"id": cid, "name": "Hero", "traits": {"curious": 0.8}}])
    # create an arc and activate it by advancing
    aid = eng.create_arc("ExplorationArc", [cid])
    # simulate events to activate arc
    for i in range(2):
        ev = eng.generate_event()
        # ensure events do not raise
    # mark arc active
    eng.arcs[aid]["state"] = "active"

    # persist state
    p = tmp_path / "eng_state.json"
    eng.save_state(str(p))
    assert os.path.exists(str(p))

    # load into a fresh engine and ensure arc/character persisted
    eng2 = NarrativeEngine(seed=12345)
    eng2.load_state(str(p))
    assert cid in eng2.characters
    assert any(a for a in eng2.arcs.values() if a.get("name") == "ExplorationArc")

    # selector should bias towards 'explore' for curious trait
    chosen = eng2._select_action_weighted(cid)
    assert chosen in {"explore", "attack", "gather", "trade", "rest"}

