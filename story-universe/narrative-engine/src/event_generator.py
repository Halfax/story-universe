# Evo-X2 Tick Subscriber and Basic Event Generator
import zmq
import requests
import time
import random

PI_API = "http://192.168.0.84:8001/event"  # Update with actual Pi IP if needed
TICK_SUB_ADDR = "tcp://192.168.0.84:5555"  # Pi's PUB address

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(TICK_SUB_ADDR)
socket.setsockopt_string(zmq.SUBSCRIBE, "")

print("[Evo-X2] Tick subscriber started. Waiting for ticks...")

while True:
    msg = socket.recv_json()
    if msg.get("type") == "system_tick":
        print(f"[Evo-X2] Received tick: {msg}")
        # Generate a simple event
        event = {
            "type": "character_action",
            "timestamp": msg.get("timestamp", int(time.time())),
            "character_id": str(random.choice([1, 2, 3])),
            "location_id": str(random.choice([100, 200, 300])),
            "description": "Auto-generated event from Evo-X2"
        }
        try:
            resp = requests.post(PI_API, json=event, timeout=3)
            print(f"[Evo-X2] Sent event, status: {resp.status_code}, response: {resp.text}")
        except Exception as e:
            print(f"[Evo-X2] Failed to send event: {e}")
