Chronicle Keeper - Recent Changes

This file summarizes recent edits made by the developer agent.

- Added `CanonicalEvent` Pydantic model at `src/models/canonical_event.py` and enforced it at the FastAPI `/event` endpoint to provide stricter ingress validation and a canonical event shape.
- Fixed missing `import json` in `src/services/clock.py` (used when writing tick metadata to the database).
- Enhanced `src/messaging/publisher.py` (`ZmqPub`/`TickPublisher`) with a bounded send queue and background sender thread to provide lightweight backpressure handling under high throughput.
- Improved `narrative-engine/src/event_generator.py` to prefer planner-suggested events when available and to filter out dead characters from selection pools.
- Added unit tests under `chronicle-keeper/tests/` for `CanonicalEvent`, `ContinuityValidator`, `NarrativeEngine.generate_event`, and publisher queue behavior.

- Added `narrative-engine/src/__init__.py` to make the narrative package importable in tests.
- Narrative Engine improvements: planner-first adoption, per-character cooldowns, active arc management, and state-aware event weighting to reduce pure randomness and improve story coherence.
- Tests: added clock-specific and serialization edge-case tests; test infra (`chronicle-keeper/tests/conftest.py`) now sets `CHRONICLE_DISABLE_CLOCK=1` and injects local `src` paths for reliable test runs.

Notes:
- The `/event` endpoint now accepts a `CanonicalEvent` model; existing clients should still work provided they send compatible JSON.
- The publisher uses a non-blocking enqueue; when the send queue is full messages will be dropped and counted as errors. This avoids blocking event producers under load.

Recommended next steps:
- Add CI workflow to run tests in a reproducible environment.
- Expand unit tests for serialization and edge-cases in `ContinuityValidator`.
- Consider persisting the send-queue to disk or a durable broker for guaranteed delivery if needed.
