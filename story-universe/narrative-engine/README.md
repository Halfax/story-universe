# Narrative Engine (Evo-X2)

Quick runner and docs for the Narrative Engine.

Requirements
- Python 3.11+
- See `requirements.txt` in this folder (includes `requests`, `pyzmq`)

Run modes
- Interval mode (default): generates an event every `TICK_INTERVAL` seconds.
  ```bash
  export CHRONICLE_BASE_URL=http://127.0.0.1:8001
  export TICK_INTERVAL=5
  python -m src.main
  ```

- ZeroMQ tick-driven mode: subscribe to Pi tick publisher and generate on each tick.
  ```bash
  export CHRONICLE_BASE_URL=http://pi.local:8001
  export USE_ZMQ_TICKS=1
  export ZMQ_PUB_CLIENT_ADDR=tcp://pi.local:5555
  python -m src.main
  ```

Notes
- `event_generator.py` persists internal engine state to `src/engine_state.json` (cooldowns, active arcs, last_event).
- The generator queries the Chronicle Keeper for `world/state`, `world/characters`, `world/locations`, and `world/factions`.
- This runner is intentionally lightweight — replace or extend generation logic as your narrative needs grow.

Character Goals / Motivation
- The generator supports a simple per-character goals system which influences event selection:
  - Goals are inferred from an explicit `goals` field on a character or from common `traits` (e.g., `curious` -> `explore`).
  - Goals are stored in `src/engine_state.json` under `char_goals` and include `goal`, `progress`, and `assigned_at`.
  - Characters with active goals are preferred when sampling participants for events; goals progress when the character is involved in events and are resolved after several progress steps.

Example: to have a character drive exploration, include a `traits` or `goals` entry in the Chronicle Keeper character record. The Narrative Engine will pick up the goal on next fetch.

Next improvements
- Drive actions from explicit character goals/motivations (not yet implemented in the generator).
- Add more robust retry/backoff and metrics for event publishing.

Tick Subscriber
 - **Purpose:** `src/tick_subscriber.py` listens for `system_tick` messages from the Chronicle Keeper (Pi) via ZeroMQ and triggers the Narrative Engine to generate and POST events.
 - **Run (from repo root or `narrative-engine` folder):**
   - Activate venv (PowerShell):
     ```powershell
     narrative-engine\venv\Scripts\Activate.ps1
     ```
   - Run the subscriber:
     ```bash
     python -m src.tick_subscriber
     ```
 - **Notes:**
   - The subscriber reads the subscribe address from `src.config` (`ZMQ_SUB_ADDR`) which falls back to `tcp://127.0.0.1:5555`.
   - It only reacts to messages where `type == 'system_tick'` and will generate/send one event per tick.
   - Run this as a long-running service (systemd, supervisor, or Docker entrypoint) on Evo‑X2 to connect to the Pi's tick publisher.

## Usage: Quick Start (generate one event)

Run a simple smoke test to generate one event locally. By default the generator posts to `http://localhost:8001` (Chronicle Keeper).

Windows (PowerShell):

```powershell
cd story-universe/narrative-engine
.\venv\Scripts\Activate.ps1    # or: .\venv\Scripts\activate
pip install -r requirements.txt
cd src
python event_generator.py
```

Linux/macOS:

```bash
cd story-universe/narrative-engine
source venv/bin/activate
pip install -r requirements.txt
cd src
python event_generator.py
```

Notes:
- The lightweight embeddings helper is at `src/generators/embeddings.py` and the planner is `src/generators/narrative_planner.py`.
- To change the Chronicle Keeper target, instantiate `NarrativeEngine(pi_base_url="http://your-pi:8001")` in code.
