# Story‑Universe Consolidated TODO

## Core Development

### High Priority
- [ ] **Event System**
  - [x] Define base event structure
  - [x] Implement event validation
  - [x] Add event handlers and middleware
  - [x] Document event types and schemas

- [ ] **Shared Models**
  - [x] Base Model and Event classes
  - [x] Character model with validation
  - [x] Location model with coordinates
  - [x] Item and Inventory system
  - [x] Model serialization/deserialization
  - [ ] Unit tests for all models

- [ ] **Validation System**
  - [x] Core validation framework
  - [x] Common validators (Range, Length, Regex, etc.)
  - [x] Conditional and composite validators
  - [x] Documentation and examples
  - [ ] Performance optimization

### Medium Priority
- [ ] **Tick Publisher**
  - [x] Basic implementation
  - [ ] Error recovery
  - [ ] Backpressure handling
  - [ ] Performance testing

- [ ] **Continuity Validator**
  - [ ] Define validation rules
  - [ ] Implement timeline checks
  - [ ] Add narrative constraints
  - [ ] Performance optimization

- [ ] **Narrative Engine**
  - [ ] Redesign architecture
  - [ ] Implement event processing
  - [ ] Add story arc management
  - [ ] Improve character AI

## Infrastructure
### Development Environment
- [ ] Set up CI/CD pipeline
  - [ ] GitHub Actions workflow
  - [ ] Automated testing
  - [ ] Code coverage reporting
- [ ] Docker Configuration
  - [x] Basic Dockerfiles
  - [ ] Optimize container size
  - [ ] Multi-stage builds
  - [ ] Health checks

### Deployment
  - [ ] systemd service files
  - [ ] Log rotation
  - [ ] Auto-start on boot

## World Browser / Frontend

- [ ] Implement world-browser mock mode
  - Provide `MOCK_MODE=1` to run UI without Pi/backend
  - Add lightweight mock API server for local development (completed)
  - Mock server: [world-browser/src/mock_api.py](world-browser/src/mock_api.py#L1-L200)

- [ ] Implement world-browser API integration
  - Connect to `GET /world` and `POST /event` endpoints (in progress)
  - Add API key handling for authenticated actions (implemented)

- [ ] World Browser UI components
  - Event timeline view (implemented)
  - Character panel (implemented)
  - Location map (implemented)
  - Filters (not started)
  - Visualization: relationship graph (implemented)
  - Visualization: event arcs (implemented in timeline)

- [ ] World Browser polling optimization
  - Exponential backoff (implemented)
  - Delta polling (not started)
  - WebSocket upgrade option (not started)

- [ ] World Browser packaging & docs
  - Developer README (updated)
  - Packaging instructions (Electron/web) (not started)

- [ ] Add frontend tests
  - Mock API tests (implemented)
  - UI integration / Qt tests (not started)

## Documentation

### Technical Documentation
- [x] Validation system
- [ ] API Reference
- [ ] Deployment guides

### Developer Resources
- [ ] Tutorials
- [ ] Example projects
- [ ] Troubleshooting guide

## Testing & Quality
### Unit Tests
- [x] Core utilities
- [ ] Model validation
- [ ] API endpoints

 - [ ] Validate causation/correlation chains and event preconditions
 - [x] Upgrade event generator to weighted, state-aware logic
 - [x] Implement personality-based gating and wiring of faction metrics into generator
### Integration Tests
- [ ] Component interactions
- [ ] End-to-end scenarios
- [ ] Performance testing

## Security

### Authentication & Authorization
- [ ] API key management
- [ ] Role-based access control
- [ ] Rate limiting

### Data Protection
- [ ] Encryption at rest
- [ ] Secure configuration
- [ ] Audit logging

## Next Steps

### Immediate Priorities
1. Complete event system implementation
2. Finish shared models implementation
3. Set up CI/CD pipeline
4. Improve test coverage

### Help Wanted
- [ ] Implement event handlers
- [ ] Add model serialization tests
- [ ] Write API documentation
- [ ] Create deployment guides

---

*Last Updated: 2026-01-12*

## Agent Tracker Snapshot (2026-01-12)

The agent's internal tracker (live):

- [x] Fix `apply_event_consequences` to use `severity`/`stability` (completed)
- [ ] Defer running chronicle-keeper tests (user requested)
- [ ] Add unit tests for consequence-scaling (trust/relationships/personality)
- [ ] Make background services test-friendly (config/env to shorten sleeps)

This snapshot reflects the agent-run task tracker and is provided for visibility. Remove or update this section as you prefer.

### Synchronized Master Agent Tracker (2026-01-12)

The master agent tracker below is kept in sync with the repository `TODO.md` and the assistant's internal tracker. Items the agent marked as completed are noted.

- [ ] Implement event validation
- [ ] Finish shared models
- [ ] Add inventory system
- [ ] Expand continuity validator
- [ ] Add tick publisher recovery
- [ ] Narrative engine redesign
- [ ] Persist story arcs
- [ ] Set up CI/CD pipeline
- [ ] Optimize Dockerfiles
- [ ] Write API reference docs
- [ ] Increase unit test coverage
- [ ] Add integration tests
- [ ] Add authentication & RBAC
- [ ] Seed world data into Pi
- [ ] Add World Browser mock-mode

- [x] Fix PySide6 QAction imports in world-browser UI
- [x] Fix visualization imports in world-browser UI
- [x] Document World Browser polling integration
- [x] Add causation/correlation metadata to generated events
- [x] Seed fallback characters/locations and add send validation

-- Agent note: I will keep this tracker and `TODO.md` synchronized. When I complete or update any task above I will immediately update this section and the internal tracker so nothing is missed.

## From Random Chaos → Coherent Narrative Engine (Proposed Roadmap)

This is a phased implementation plan to move from the current random-sampler Narrative Engine to a state-aware, coherent narrative system.

Phase 1 — Wire in the Faction State Model (foundation)
1. Create persistent faction state tables:
  - `factions`, `faction_relationships`, `faction_attributes`, `faction_history` (optional)
2. Define canonical relationship types: `ally`, `neutral`, `hostile`, `vassal`, `protectorate`, `unknown`
3. Add numeric relationship metrics: `trust` (0–100), `hostility` (0–100), `influence` (0–100)
4. Add cooldown timestamps: `last_alliance`, `last_conflict`, `last_recruitment`
5. Add faction goals/personality traits: `expansionist`, `isolationist`, `mercantile`, `mystical`, `militaristic`

Phase 2 — Build the Continuity Validator (Pi)
6. Validate faction existence and names (reject nonexistent/malformed/self-targeting)
7. Validate relationship logic (no forming alliance if already allied, no declaring war if already at war)
8. Enforce cooldowns (prevent flipping alliances/wars every tick)
9. Validate causation/correlation chains (follow-ups reference valid prior events)
10. Validate character and location involvement where required

Phase 3 — Upgrade the Event Logic Engine
11. Replace random sampler with weighted logic using faction goals, relationships, history, world tension, proximity
12. Add event preconditions (explore→location, conflict→hostility>threshold, etc.)
13. Add event consequences (update trust, hostility, influence, cooldowns, faction history)
14. Add multi-step narrative arcs (tension→skirmish→war→treaty, exploration arcs, alliances→betrayal)

Phase 4 — Add Character & Location Involvement
15. Character selection logic: pick faction members, ensure alive/available, assign roles
16. Location selection logic: pick meaningful, appropriate locations
17. Update character & location state (movement, injuries, map knowledge)

Phase 5 — Add Causation & Correlation IDs
18. Assign `causationId` for follow-ups
19. Assign `correlationId` to group related events
20. Add arc tracking (names, states, participants)

Phase 6 — Testing, Validation, and Telemetry
21. Add verbose logging for rejected events (reason, offending fields, suggested fix)
22. Add simulation replay mode (ticks without writing to DB)
23. Add dashboards: relationship graph, event frequency, arc progression
24. Add smoke tests to ensure no invalid events pass and valid events are accepted

Phase 7 — Turn It On
25. Enable state-aware generation (disable random sampler, enable planner, strict validator)
26. Observe coherent storylines and iterate

Add this roadmap to the master tracker? The agent will convert these phases into concrete tasks and keep `TODO.md` updated as work progresses.

## Reviewed Plan & Recommendations

Summary review (2026-01-12): the master TODO correctly lists the major workstreams. To make progress predictable, break the top priorities into short, testable phases and add CI gate checks before merging large changes.

Prioritized next actions (short-term, 1–2 weeks):

- **1 — Event Validation (high priority)**: implement validation middleware in `chronicle-keeper/src/services/continuity.py` to enforce schema, `causationId`/`correlationId` presence, and basic character/location existence. Add unit tests under `chronicle-keeper/tests/`.
- **2 — Shared Models & Serialization (high priority)**: finish `shared/models/item.py` and add `to_dict`/`from_dict` + roundtrip tests.
- **3 — CI Pipeline (high priority)**: add GitHub Actions workflow that runs `pytest` for `chronicle-keeper` and `unittest` for `narrative-engine` on PRs.
- **4 — Narrative Engine: planner & persistence (medium)**: persist story arcs in `engine_state.json` or Pi `character_state`; prefer planner-generated events when available.

Medium-term (2–6 weeks):
- Implement inventory service and transactional `item_use` flow in `chronicle-keeper`.
- Harden Tick Publisher: backoff/reconnect, metrics, and durable queue option (or broker).
- Expand continuity rules: faction/location constraints, contradiction detection.

Operational items:
- Add a `--mock` or `MOCK_MODE=1` flag for the World Browser and Narrative Engine to enable local development without Pi.
- Add deployment docs and optional `systemd` unit for Pi (see `AGENTS.md`).

Success criteria for the next milestone:
- `POST /event` rejects invalid events with clear messages and tests cover edge cases.
- CI passes on every PR and runs the validator unit tests.
- The World Browser shows meaningful events with characters and locations (no ungrounded random events).

If you approve this refined plan I will add the concrete tasks (with file/line targets) to the agent tracker and start implementing the highest-priority item: **Event Validation**.
