		---
		## Roadmap: Next Tracks

		🟦 Track 1 — Bring the Narrative Engine to Life (Evo‑X2)
		Phase 1: Basic Event Generator
			- Subscribe to Pi ticks
			- On each tick, generate a simple event
			- Send event → Pi /event endpoint
			- Log success/failure
		Phase 2: Character‑Aware Logic
			- Load characters from Pi
			- Generate actions based on traits
			- Move characters between locations
			- Create relationships, conflicts, alliances
		Phase 3: Narrative Planning
			- Multi‑step story arcs
			- Faction dynamics
			- Political systems
			- Emergent conflicts
			- Procedural lore

		🟦 Track 2 — Build the World Browser (Alienware)
		Phase 1: Basic UI
			- List recent events
			- Show world time
			- Show characters + locations
		Phase 2: Visual Maps
			- 2D map of the world
			- Character positions
			- Faction territories
		Phase 3: Relationship Graphs
			- Character webs
			- Faction alliances
			- Event chains
		Phase 4: Timeline Explorer
			- Scrollable timeline
			- Filters
			- Event categories
			- Story arcs

		🟩 Track 3 — Expand the Chronicle Keeper (Pi)
		Phase 1: Richer Validation
			- Character state transitions
			- Faction rules
			- Location constraints
			- Timeline consistency
			- Duplicate detection
		Phase 2: World Rules Engine
			- Magic systems
			- Physics
			- Political structures
			- Cultural rules
		Phase 3: Query Enhancements
			- Pagination
			- Filtering
			- Search
			- Event categories
			- Character histories

		🌠 The Big Picture
		You now have:
		- a heartbeat (Pi world clock)
		- a memory (Pi database)
		- a messaging system (ZeroMQ)
		- a log aggregation system (Evo‑X2)
		- a canonical event pipeline (Pi validator)
		- a distributed architecture ready for expansion
		The next steps are about breathing life into the world.
		- Event broadcasting is now active: accepted events are sent to other nodes using the TickPublisher (ZeroMQ PUB).
	- Tick broadcasting is now wired: each tick is sent to other nodes using the TickPublisher (ZeroMQ PUB).
 Next Step Options

✅ The Pi (Chronicle Keeper) foundation and all core skeleton files/stubs are now in place:
- FastAPI app, DB schema, shared models, API/service/messaging stubs, Dockerfile, requirements, config

✅ A) Continuity validator logic file (continuity.py) created in services. Begin implementing event validation logic next.
B) Build the tick broadcaster (Pi → Evo‑X2 communication)
C) Build the Evo‑X2 narrative engine skeleton
D) Build the Alienware world browser skeleton



✅ 1. World Clock + Tick Broadcasting stub implemented in services/clock.py.
	- Scheduler loop, canonical world time in DB, tick logging as system event.
	- Ready for future /tick broadcast to Evo‑X2.

🟥 2. Expand the Continuity Validator
Right now it's basic. Next step is to make it lore‑aware.
Add checks for:
- Character existence
- Character location consistency


🟩 3. Query Endpoints for Other Nodes implemented:
	- /world/state, /world/characters, /world/locations, /world/events/recent now available.
	- Alienware and Evo‑X2 can now read the world state for visualization and simulation.


🟦 4. Event Types + Canonical Models implemented:
	- Canonical event types and a Pydantic CanonicalEvent model are now defined in shared/models/event_types.py.
	- Ready for structured event validation and generation by Evo‑X2.


🟥 5. Messaging Integration started:
	- ZeroMQ tick publisher stub implemented in messaging/publisher.py.
	- Ready to broadcast ticks and events to Evo‑X2 and other nodes.
Add:
- ZeroMQ or MQTT publisher for ticks
- Subscriber for Evo‑X2 responses

🟩 6. Add Persistence for Characters, Factions, Locations
Right now you have the schema — now you need the CRUD.
Add endpoints:
- /character/create
- /character/update

🟦 7. Add a "World Rules" Module
This is where you encode the laws of your universe.
Examples:
- magic system rules
- physics constraints

---

The current event generator is too random and basic. It needs a major overhaul:
 For detailed tasks and priorities, please refer to `TODO.md`.
**Problems:**
- Pure randomness - all engines use random.choice() with no weighting or context
- No world state awareness - does not check current relationships, tensions, or history
- Hardcoded data - factions are static strings, locations are hardcoded IDs
- Flat priority fallback - no strategic decision about what should happen now
- No tension/pacing - every tick generates something random
- No memory - does not track ongoing arcs, unfinished conflicts
- Trait mapping is trivial - characters feel identical

**Required Improvements:**
- [ ] Query Pi for world state before generating (know current tensions, active arcs, character locations)
- [ ] Weight event types by narrative need (low tension -> start conflict; high -> escalate or resolve)
- [ ] Track active story arcs and advance them (do not start random new ones)
- [ ] Use real faction/location data from Chronicle Keeper
- [ ] Character goals/motivations should drive actions, not just traits
- [ ] Add cooldowns - do not spam the same event types
- [ ] Add cause-and-effect logic - events should follow from previous events
