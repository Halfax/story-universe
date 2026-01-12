World Browser — Mock Mode
=========================

This project includes a lightweight mock API server for local World Browser UI development.

Why: use `MOCK_MODE=1` in the UI to develop the frontend without a running Chronicle Keeper instance.


Running the mock server

1. Install dependencies:

```powershell
python -m pip install fastapi uvicorn
```

2. Start the mock server (from repository root):

```powershell
uvicorn world_browser.src.mock_api:app --reload --port 8002
```

Use with the real backend

If you prefer to run the real Chronicle Keeper backend locally and point the World Browser at it, do the following.

1. Run the Chronicle Keeper backend (uvicorn) from the `chronicle-keeper` package root:

```powershell
cd story-universe/chronicle-keeper
python -m pip install -r requirements.txt
uvicorn story_universe.chronicle_keeper.src.main:app --reload --host 127.0.0.1 --port 8001
# OR, from repo root (module import path already used in examples):
uvicorn story-universe.chronicle-keeper.src.main:app --reload --host 127.0.0.1 --port 8001
```

2. Alternatively, build & run the Docker image (repo root):

```powershell
docker build -t chronicle-keeper -f story-universe/chronicle-keeper/Dockerfile story-universe/chronicle-keeper
docker run -p 8001:8001 --env CHRONICLE_AUTO_IMPORT=1 chronicle-keeper
```

3. Point the World Browser UI to the real backend by setting `CHRONICLE_BASE_URL` (default is `http://127.0.0.1:8001`) and disabling `MOCK_MODE`:

```powershell
$env:CHRONICLE_BASE_URL = "http://127.0.0.1:8001"
$env:MOCK_MODE = "0"
```

Primary real endpoints used by the UI

- `GET /world/state` — canonical world snapshot (preferred)
- `GET /world/events/recent` — recent events (supports `limit`, `offset`, `event_type`, `character_id`, `location_id`)
- `POST /event` — ingest canonical events (accepts `CanonicalEvent` shape; server may auto-generate `id`)

Notes

- When integrating with the real backend, the UI will attempt the canonical endpoints first. If you run into shape differences, I can harden the UI to map/translate responses.
- Use `CHRONICLE_API_KEY` if the Chronicle Keeper is configured to require an API key; the UI sends this as `X-API-Key` when present.

# World Browser UI

This document describes the World Browser UI (`world-browser/src`) and how it connects to the Chronicle Keeper to display events.

Overview
- The World Browser is a PySide6-based desktop UI providing an Event Log and Timeline view.
- The UI polls the Chronicle Keeper `/world/events/recent` endpoint and renders events in the timeline and event log.

How it fetches data
- `MainWindow` starts a QTimer (2s interval) that requests `CHRONICLE_BASE_URL + /world/events/recent`.
- New events are deduplicated by `id` and added to the `EventLogPanel` and `TimelinePanel`.
- Timeline placement uses the event `timestamp` field.

Configuration
- By default the UI targets `http://127.0.0.1:8001`.
- Override with environment variable `CHRONICLE_BASE_URL`, e.g.:

  PowerShell:
  ```powershell
  $env:CHRONICLE_BASE_URL = 'http://pi-host:8001'
  python -m ui.main_window
  ```

  Bash:
  ```bash
  export CHRONICLE_BASE_URL='http://pi-host:8001'
  python -m ui.main_window
  ```

Notes & limitations
- The poller uses a simple HTTP GET and has a short timeout; it is intended for local/dev usage only.
- If the Chronicle Keeper is unreachable the UI silently continues polling.
- Event rendering assumes `timestamp` is a Unix timestamp in seconds.
- This is a lightweight integration — consider switching to ZeroMQ or WebSocket for real-time production usage.

Files modified
- `ui/main_window.py` — added polling logic, env configuration, and event-to-timeline mapping.

Next improvements (optional)
- Add configurable poll interval and backoff on failures.
- Use a background thread or async I/O to avoid any UI-blocking during slow HTTP calls.
- Add a mock-mode to show sample events when Pi is unreachable.

