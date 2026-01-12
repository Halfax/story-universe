# Evo-X2 Tick Subscriber and Basic Event Generator
import zmq
import requests
import time
import random
from generators.character_gen import CharacterManager
from generators.action_gen import ActionGenerator
from generators.movement_engine import MovementEngine
from generators.relationship_engine import RelationshipEngine
from generators.narrative_planner import NarrativePlanner
from generators.faction_engine import FactionEngine

PI_API = "http://localhost:8001/event"  # Updated to actual Pi IP
TICK_SUB_ADDR = "tcp://localhost:5555"  # Updated to actual Pi IP

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(TICK_SUB_ADDR)
socket.setsockopt_string(zmq.SUBSCRIBE, "")



# Initialize managers
character_manager = CharacterManager()
character_manager.fetch_characters()
action_generator = ActionGenerator(character_manager)
movement_engine = MovementEngine(character_manager)
relationship_engine = RelationshipEngine(character_manager)
narrative_planner = NarrativePlanner(character_manager)
faction_engine = FactionEngine(character_manager)

print("[Evo-X2] Tick subscriber started. Waiting for ticks...")

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

try:
    while True:
        socks = dict(poller.poll(500))  # 500 ms timeout
        if socket in socks and socks[socket] == zmq.POLLIN:
            msg = socket.recv_json()
            if msg.get("type") == "system_tick":
                print(f"[Evo-X2] Received tick: {msg}")
                # --- Faction Logic ---
                # Try to generate a faction event
                faction_event = faction_engine.generate_faction_event()
                if faction_event:
                    event = {
                        "type": "faction_event",
                        "timestamp": msg.get("timestamp", int(time.time())),
                        "faction": faction_event['faction'],
                        "action": faction_event['action'],
                        "target": faction_event['target'],
                        "summary": faction_event['summary'],
                        "description": faction_event['summary']
                    }
                else:
                    # Fallback to narrative planning event
                    plan = narrative_planner.generate_plan()
                    if plan:
                        event = {
                            "type": "narrative_plan",
                            "timestamp": msg.get("timestamp", int(time.time())),
                            "arc": plan['arc'],
                            "characters": plan['characters'],
                            "summary": plan['summary'],
                            "description": f"Narrative arc '{plan['arc']}' involving {', '.join(plan['characters'])}: {plan['summary']}"
                        }
                    else:
                        # Fallback to relationship event
                        relationship = relationship_engine.update_relationships()
                        if relationship:
                            event = {
                                "type": "relationship_update",
                                "timestamp": msg.get("timestamp", int(time.time())),
                                "character_id": str(relationship['character_id']),
                                "target_id": str(relationship['target_id']),
                                "change": relationship['change'],
                                "description": f"Relationship between {relationship['character_id']} and {relationship['target_id']} {relationship['change']}d."
                            }
                        else:
                            # Fallback to movement event
                            movement = movement_engine.move_character()
                            if movement:
                                event = {
                                    "type": "character_movement",
                                    "timestamp": msg.get("timestamp", int(time.time())),
                                    "character_id": str(movement['character_id']),
                                    "new_location": str(movement['new_location']),
                                    "description": f"Character {movement['character_id']} moved to {movement['new_location']}"
                                }
                            else:
                                # Fallback to action event if no movement
                                action_info = action_generator.generate_action()
                                if action_info:
                                    char_id = action_info['character_id']
                                    action = action_info['action']
                                    traits = action_info['traits']
                                    loc_id = random.choice([100, 200, 300])  # TODO: Use real location logic
                                else:
                                    char_id = str(random.choice([1, 2, 3]))
                                    action = 'wait'
                                    traits = []
                                    loc_id = str(random.choice([100, 200, 300]))
                                event = {
                                    "type": "character_action",
                                    "timestamp": msg.get("timestamp", int(time.time())),
                                    "character_id": str(char_id),
                                    "location_id": str(loc_id),
                                    "action": action,
                                    "traits": traits,
                                    "description": f"{action.capitalize()} action generated for character {char_id}"
                                }
                try:
                    resp = requests.post(PI_API, json=event, timeout=3)
                    print(f"[Evo-X2] Sent event, status: {resp.status_code}, response: {resp.text}")
                except Exception as e:
                    print(f"[Evo-X2] Failed to send event: {e}")
except KeyboardInterrupt:
    print("[Evo-X2] Exiting on Ctrl+C")
