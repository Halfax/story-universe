import importlib, importlib.util
from pathlib import Path


# Robust loader: locate `event_generator.py` under a nearby `narrative-engine/src` and load module from path.
def _load_narrative_engine():
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / 'narrative-engine' / 'src' / 'event_generator.py'
        if candidate.exists():
            spec = importlib.util.spec_from_file_location('narrative_event_generator', str(candidate))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.NarrativeEngine
    # If not found, raise ImportError so test harness reports clearly.
    raise ImportError("Could not locate narrative-engine/src/event_generator.py")


def test_generate_event_basic():
    NarrativeEngine = _load_narrative_engine()
    eng = NarrativeEngine(pi_base_url="http://localhost:9999")
    ev = eng.generate_event()
    assert ev is None or isinstance(ev, dict)
    if isinstance(ev, dict):
        assert "id" in ev and "type" in ev

