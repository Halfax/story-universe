# Evo-X2 Log Collector (ZeroMQ SUB)
import zmq
import json
from src.config import ZMQ_PUB_CLIENT_ADDR

LOG_FILE = "central_logs.txt"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(ZMQ_PUB_CLIENT_ADDR)  # Pi's PUB address (from config)
socket.setsockopt_string(zmq.SUBSCRIBE, "")

print("[Evo-X2] Central log collector started. Waiting for logs...")

with open(LOG_FILE, "a") as f:
    while True:
        msg = socket.recv_json()
        f.write(json.dumps(msg) + "\n")
        f.flush()
        print(f"[LOG] {msg}")
