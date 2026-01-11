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
│   │   │   ├── validator.py         # Contradiction checker
│   │   │   └── canon.py             # Canon enforcement rules
│   │   └── messaging/
│   │       ├── __init__.py
│   │       └── publisher.py         # ZeroMQ/MQTT tick publisher
│   ├── tests/
│   ├── config.yaml
│   ├── requirements.txt
│   └── Dockerfile
│
├── narrative-engine/                # Evo-X2 Max+
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # Engine entry point
│   │   ├── generators/
│   │   │   ├── __init__.py
│   │   │   ├── event_generator.py   # Creates new events
│   │   │   ├── character_gen.py     # Creates characters
│   │   │   ├── dialogue_gen.py      # Generates dialogue
│   │   │   └── lore_gen.py          # Expands worldbuilding
│   │   ├── simulation/
│   │   │   ├── __init__.py
│   │   │   ├── politics.py          # Political simulation
│   │   │   ├── economy.py           # Economic systems
│   │   │   ├── conflicts.py         # War/conflict resolution
│   │   │   └── relationships.py     # Character relationship dynamics
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py        # LLM API wrapper
│   │   │   ├── embeddings.py        # Embedding model
│   │   │   ├── prompts/
│   │   │   │   ├── event.txt
│   │   │   │   ├── character.txt
│   │   │   │   └── dialogue.txt
│   │   │   └── narrative_planner.py # Story arc planning
│   │   └── messaging/
│   │       ├── __init__.py
│   │       ├── subscriber.py        # Listens for ticks
│   │       └── api_client.py        # Calls Pi's API
│   ├── tests/
│   ├── config.yaml
│   ├── requirements.txt
│   └── Dockerfile
│
├── world-browser/                   # Alienware 18
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
