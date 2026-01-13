# Narrative Engine (Minimal Implementation)

Overview
--------
A lightweight Narrative Engine lives at `narrative-engine/src/event_generator.py`.
It provides a small `NarrativeEngine` class with:

- `generate_event()` — produce a simple event (or `None`) for testing.
- `seed_characters()` — load characters with optional traits to drive basic AI.
- `create_arc()` / `advance_arc()` — minimal in-memory story-arc support.
- `process_external_event()` — accept external events to influence arcs/traits.

- Persistence: `save_state(path)` and `load_state(path)` persist `arcs` and `characters` to disk for long-term arc tracking.
- Selector/Planner: a small weighted selector (`_select_action_weighted`) biases actions by arc urgency and character traits; `generate_event()` uses this selector.

Design notes
------------
This implementation is intentionally small and test-friendly. It can be extended
into the full planner/selector/persona/arc layers from the roadmap.

Usage example
-------------
```python
from narrative_engine.src.event_generator import NarrativeEngine

eng = NarrativeEngine(seed=42)
eng.seed_characters([{"id": "c1", "name": "Ava", "traits": {"curious": 0.7}}])
ev = eng.generate_event()
```

Extending
---------
- Replace the randomness-based chooser with a planner that consults faction goals,
  location context, and arc objectives.
- Persist `arcs` to DB for long-term story tracking.
- Add a scheduler to produce events at configured tick intervals rather than
  being polled via `generate_event()`.

Testing
-------
The test harness `tests/test_narrative_engine.py` loads the `NarrativeEngine`
module from the repository path and asserts that `generate_event()` returns
either `None` or a dictionary containing at least `id` and `type`.
