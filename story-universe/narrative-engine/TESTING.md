# Testing Narrative Engine

Run the unit tests for the Narrative Engine with Python's builtin `unittest`.

From the repo root (or the `narrative-engine` folder):

```bash
python -m unittest discover -s narrative-engine/tests -v
```

What the tests cover
- `test_event_generator.py`:
  - `test_generate_event_without_pi`: ensures the generator still produces an event when the Chronicle Keeper is unreachable.
  - `test_goals_influence_selection_and_progress`: mocks Pi responses to validate goal inference from traits and that goals progress over generated events.

Notes
- Tests mock HTTP calls to the Chronicle Keeper; they do not require a running Pi instance.
- If you use a virtual environment, ensure dependencies from `narrative-engine/requirements.txt` are installed.
