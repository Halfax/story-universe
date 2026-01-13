"""Shim config for chronicle-keeper src package.
Imports values from shared.config when available, otherwise falls back to env vars.
"""

import os

try:
    from shared.config import (
        CHRONICLE_IP,
        CHRONICLE_HOST,
        CHRONICLE_PORT,
        CHRONICLE_BASE,
        CHRONICLE_API_PATH,
        CHRONICLE_API_URL,
        CHRONICLE_DB_PATH,
        ZMQ_PUB_BIND_ADDR,
        ZMQ_PUB_CLIENT_ADDR,
        ZMQ_SUB_ADDR,
        TICK_PORT,
        TICK_PUBLISHER_RECONNECT_DELAY,
    )
except Exception:
    CHRONICLE_IP = os.getenv("CHRONICLE_IP", "127.0.0.1")
    CHRONICLE_HOST = os.getenv("CHRONICLE_HOST", "0.0.0.0")
    CHRONICLE_PORT = int(os.getenv("CHRONICLE_PORT", "8001"))
    CHRONICLE_BASE = os.getenv(
        "CHRONICLE_BASE_URL", f"http://{CHRONICLE_IP}:{CHRONICLE_PORT}"
    )
    CHRONICLE_API_PATH = os.getenv("CHRONICLE_API_PATH", "/event")
    CHRONICLE_API_URL = os.getenv(
        "CHRONICLE_API_URL", f"{CHRONICLE_BASE}{CHRONICLE_API_PATH}"
    )
    CHRONICLE_DB_PATH = os.getenv("CHRONICLE_KEEPER_DB_PATH", "/data/chronicle.db")
    ZMQ_PUB_BIND_ADDR = os.getenv(
        "ZMQ_PUB_BIND_ADDR", f"tcp://*:{os.getenv('ZMQ_PORT','5555')}"
    )
    ZMQ_PUB_CLIENT_ADDR = os.getenv(
        "ZMQ_PUB_CLIENT_ADDR", f"tcp://{CHRONICLE_IP}:{os.getenv('ZMQ_PORT','5555')}"
    )
    ZMQ_SUB_ADDR = os.getenv("ZMQ_SUB_ADDR", ZMQ_PUB_CLIENT_ADDR)
    TICK_PORT = int(os.getenv("ZMQ_PORT", "5555"))
    TICK_PUBLISHER_RECONNECT_DELAY = float(
        os.getenv("TICK_PUBLISHER_RECONNECT_DELAY", "5.0")
    )
