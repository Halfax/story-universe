import os

# Central shared configuration for host/IP and port values.
# Override using environment variables as needed.

# Network / API
CHRONICLE_IP = os.getenv("CHRONICLE_IP", "127.0.0.1")
CHRONICLE_HOST = os.getenv("CHRONICLE_HOST", "0.0.0.0")
CHRONICLE_PORT = int(os.getenv("CHRONICLE_PORT", "8001"))
CHRONICLE_BASE = os.getenv("CHRONICLE_BASE_URL", f"http://{CHRONICLE_IP}:{CHRONICLE_PORT}")
CHRONICLE_API_PATH = os.getenv("CHRONICLE_API_PATH", "/event")
CHRONICLE_API_URL = os.getenv("CHRONICLE_API_URL", f"{CHRONICLE_BASE}{CHRONICLE_API_PATH}")

# Database
CHRONICLE_DB_PATH = os.getenv("CHRONICLE_KEEPER_DB_PATH", "/data/chronicle.db")

# ZeroMQ
ZMQ_PORT = int(os.getenv("ZMQ_PORT", "5555"))
ZMQ_PUB_BIND_ADDR = os.getenv("ZMQ_PUB_BIND_ADDR", f"tcp://*:{ZMQ_PORT}")
ZMQ_PUB_CLIENT_ADDR = os.getenv("ZMQ_PUB_CLIENT_ADDR", f"tcp://{CHRONICLE_IP}:{ZMQ_PORT}")
ZMQ_SUB_ADDR = os.getenv("ZMQ_SUB_ADDR", ZMQ_PUB_CLIENT_ADDR)

# Convenience
TICK_PORT = ZMQ_PORT
