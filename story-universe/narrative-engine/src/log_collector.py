# Evo-X2 Log Collector (ZeroMQ SUB)
import zmq
import json

LOG_FILE = "central_logs.txt"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://192.168.0.84:5555")  # Pi's PUB address
socket.setsockopt_string(zmq.SUBSCRIBE, "")

print("[Evo-X2] Central log collector started. Waiting for logs...")

with open(LOG_FILE, "a") as f:
    while True:
        msg = socket.recv_json()
        f.write(json.dumps(msg) + "\n")
        f.flush()
        print(f"[LOG] {msg}")
