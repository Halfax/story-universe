# Project Structure Plan

```
story-universe/
├── shared/                          # Shared across all machines
│   ├── models/
│   │   ├── __init__.py
│   │   ├── character.py             # Character, Trait, Relationship
│   │   ├── event.py                 # Event, EventType, TickEvent
│   │   ├── location.py              # Location, Region, Map
│   │   ├── faction.py               # Faction, Alliance, Conflict
│   │   ├── world_state.py           # WorldState, WorldRules
│   │   └── timeline.py              # TimePoint, Era, Calendar
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── messages.py              # ZeroMQ/MQTT message formats
│   │   └── api_contracts.py         # API request/response schemas
│   └── utils/
│       ├── __init__.py
│       └── serialization.py         # JSON/msgpack helpers
│
├── chronicle-keeper/                # Raspberry Pi 5
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── events.py            # /add_event, /get_events
│   │   │   ├── world.py             # /get_world_state, /tick
│   │   │   ├── characters.py        # CRUD for characters
│   │   │   ├── locations.py         # CRUD for locations
│   │   │   └── factions.py          # CRUD for factions
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py          # SQLite/DuckDB connection
│   │   │   ├── schema.sql           # Table definitions
│   │   │   └── queries.py           # Query helpers
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── clock.py             # World clock / tick generator
│   │   │   ├── continuity.py        # Canonical event validator (timeline, state, relationships, lore)
│   │   │   ├── test_db_setup.py     # Test DB setup/teardown helpers (for pytest)
│   │   │   └── canon.py             # Canon enforcement rules
│   │   └── messaging/
│   │       ├── __init__.py
│   │       └── publisher.py         # ZeroMQ/MQTT tick publisher
│   ├── tests/                       # Unit and API tests (pytest)
│   │   ├── test_main.py             # API endpoint tests (uses test DB override)
│   │   ├── test_continuity.py       # Validator logic tests (timeline, state, relationships, lore)
│   ├── config.yaml
│   ├── requirements.txt             # Includes fastapi, httpx for testing
│   ├── test_chronicle.db            # (pytest only) Temporary DB for isolated test runs

## Testing & Validator Notes

- The validator (continuity.py) now enforces:
	- Event type presence
	- Character state transitions (no dead→alive, no state change for dead, no duplicate state)
	- Relationship constraints (no self, forbidden types)
	- Faction rules (no attack ally, no alliance with enemy, betrayal only if either side is rival)
	- Timeline consistency (no retroactive events for character/location)
	- Location existence/constraints (forbidden/locked)
	- Lore-aware rules (magic, physics, politics)
- API and validator tests use a test DB via CHRONICLE_KEEPER_DB_PATH env var, set in test_main.py.
- test_db_setup.py creates/destroys tables for isolated test runs.
│   └── Dockerfile
│
├── narrative-engine/                # Evo-X2 Max+
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # Engine entry point
│   │   ├── generators/
│   │   │   ├── __init__.py
│   │   │   ├── event_generator.py   # Creates new events, now includes character movement logic
│   │   │   ├── character_gen.py     # Creates characters
│   │   │   ├── action_gen.py        # Generates actions based on character traits
│   │   │   ├── movement_engine.py   # Handles character movement events
│   │   │   ├── relationship_engine.py # Handles character relationship updates
│   │   │   ├── narrative_planner.py   # Handles narrative planning and story arcs
│   │   │   ├── faction_engine.py      # Handles faction logic and events

│   │   ├── ui/
│   │   │   ├── main_window.py         # Main PySide6 window (tabs: event log, timeline)
│   │   │   ├── panels/
│   │   │   │   ├── event_log.py       # Live event feed panel
│   │   │   │   ├── timeline.py        # Timeline view panel
│   │   │   │   ├── map_view.py        # World map panel
│   │   │   │   ├── character_web.py   # Character relationship graph panel
│   │   │   ├── dialogue_gen.py      # Generates dialogue
│   │   │   └── lore_gen.py          # Expands worldbuilding

│   │   ├── visualization/
│   │   │   ├── __init__.py
│   │   │   ├── map_renderer.py      # 2D map rendering (placeholder)
│   │   │   ├── graph_renderer.py    # Character web rendering (placeholder)
│   │   │   └── timeline_renderer.py # Timeline graphics

## Roadmap Progress (2026-01-11)

- [x] CharacterManager: fetch/store character data
- [x] ActionGenerator: generate actions from traits
- [x] MovementEngine: character movement logic (integrated in event_generator.py)
- [x] RelationshipEngine: relationship tracking and updates (integrated in event_generator.py)
- [x] NarrativePlanner: narrative planning and story arcs (integrated in event_generator.py)
- [x] FactionEngine: faction logic and events (integrated in event_generator.py)
- [x] World Browser UI: event log, timeline panels, main window (PySide6)
- [x] Visualization: map, character web panels, renderers (placeholders)

---


## High-Value Next Phase TODOs

### 🟩 1. Chronicle Keeper (Pi) — Deepen the Canon
- Expand Continuity Validator:
	- Timeline consistency
	- Character state transitions
	- Relationship constraints
	- Faction rules
	- Location constraints
	- Contradiction detection
	- Event deduplication
	- Lore-aware validation (magic, physics, politics)
- Add World Rules:
	- Magic system
	- Character histories
	- Faction summaries

### 🟥 2. Narrative Engine (Evo‑X2) — Bring the World to Life
- Expand Simulation Logic:
	- Faction conflicts
	- Political dynamics
	- Economic systems
	- Character motivations
	- Relationship evolution
	- Emergent events
- Narrative Planning:
	- Plot threads
	- Rising/falling tension
	- Character arcs
	- World-scale events
- Richer Character Behavior:
	- Personality traits
	- Alliances, rivalries
	- Emotional states

### 🟦 3. World Browser (Alienware) — Make the Universe Visible
- Visual Maps:
	- Character positions
	- Faction territories
	- Region overlays
- Relationship Graphs:
	- Character webs
	- Faction alliances
	- Event chains
	- Influence networks
- Timeline Explorer:
	- Scrollable timeline
	- Story arcs
	- Character-centric timelines
- UI Polish:
	- Better layout, icons, color coding, animations, tooltips, search bar
│   │   ├── simulation/
│   │   │   ├── politics.py          # Political simulation
│   │   │   ├── economy.py           # Economic systems
│   │   │   ├── conflicts.py         # War/conflict resolution
│   │   │   └── relationships.py     # Character relationship dynamics
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py        # Embedding model
│   │   │   ├── prompts/
│   │   │   │   ├── event.txt
│   │   │   │   ├── character.txt
│   │   │   └── narrative_planner.py # Story arc planning
│   │   └── messaging/
│   │       ├── __init__.py
│   │       ├── subscriber.py        # Listens for ticks
│   ├── tests/
│   ├── config.yaml
│   ├── requirements.txt
│   └── Dockerfile
├── world-browser/                   # Alienware 18

## Python Virtual Environment

- The Python venv for the Evo-X2 Narrative Engine is located at:
  - narrative-engine/venv

Activate with:
  - On Windows: narrative-engine\venv\Scripts\activate
  - On Linux/macOS: source narrative-engine/venv/bin/activate
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # App entry
│   │   ├── ui/
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py       # Main PySide6 window
│   │   │   ├── panels/
│   │   │   │   ├── timeline.py      # Timeline view
│   │   │   │   ├── map_view.py      # World map
│   │   │   │   ├── character_web.py # Relationship graph
│   │   │   │   ├── event_log.py     # Live event feed
│   │   │   │   └── faction_view.py  # Faction dashboard
│   │   │   └── dialogs/
│   │   │       ├── edit_character.py
│   │   │       ├── edit_location.py
│   │   │       └── what_if.py       # What-if scenario creator
│   │   ├── visualization/
│   │   │   ├── __init__.py
│   │   │   ├── map_renderer.py      # 2D map rendering
│   │   │   ├── graph_renderer.py    # NetworkX visualization
│   │   │   └── timeline_renderer.py # Timeline graphics
│   │   ├── api_client/
│   │   │   ├── __init__.py
│   │   │   └── chronicle_client.py  # Calls Pi's API
│   │   └── state/
│   │       ├── __init__.py
│   │       └── cache.py             # Local world state cache
│   ├── assets/
│   │   ├── icons/
│   │   ├── fonts/
│   │   └── styles.qss
│   ├── tests/
│   ├── config.yaml
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml               # Run all 3 locally for dev
├── README.md
└── pyproject.toml                   # Monorepo config (optional)
```

## Machine Deployment

| Directory          | Runs On        | Purpose              |
|--------------------|----------------|----------------------|
| `shared/`          | All machines   | Symlink or pip install |
| `chronicle-keeper/`| Raspberry Pi 5 | Canon + API + Clock  |
| `narrative-engine/`| Evo-X2 Max+    | AI + Simulation      |
| `world-browser/`   | Alienware 18   | UI + Visualization   |

## First Files to Create (Prototype Order)

1. `shared/models/event.py` — Event, TickEvent
2. `shared/models/character.py` — Character basics
3. `shared/models/world_state.py` — WorldState container
4. `chronicle-keeper/src/db/schema.sql` — Tables
5. `chronicle-keeper/src/main.py` — FastAPI with 2 endpoints
6. `narrative-engine/src/main.py` — Tick listener + simple generator
7. `world-browser/src/main.py` — Basic event log UI

## [2026-01-11] Validator Progress Update

- Relationship constraint logic (no self, forbidden types, dead/missing) is now robust and fully tested in `chronicle-keeper/src/services/continuity.py`.
- All validator tests pass (`test_continuity.py`).
- Test data and logic updated to ensure correct coverage for edge cases (string/integer IDs, alive/dead status).
- Next: Progress to faction rules, location constraints, and contradiction detection in validator.

## [2026-01-11] Validator Progress Update (cont.)

- Faction rules validation expanded: now forbids attacking allies, forming alliances with enemies, and betraying without rivalry (see tests for edge cases).
- Location constraints added: events cannot reference non-existent, forbidden, or locked locations. All relevant tests pass.
- All validator logic and tests are up to date and robust for these rules.
- Next: Add contradiction detection logic (e.g., dead characters acting, impossible state changes).

## [2026-01-11] Validator Progress Update (final for today)

- Contradiction detection added: dead characters cannot act, move, or change state; resurrection and impossible state changes are forbidden.
- All new logic is fully tested and robust (see test_continuity.py for edge cases).
- Validator now covers: timeline, state transitions, relationship constraints, faction rules, location constraints, and contradiction detection.

---
