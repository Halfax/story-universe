"""Central shared configuration used across components.

This module provides canonical configuration names and reads from
environment variables where appropriate. It replaced a legacy proxy shim
that tried to load a moved file; the canonical values now live here.
"""
from __future__ import annotations
import os
from pathlib import Path

# Chronicle / API settings
CHRONICLE_HOST = os.getenv("CHRONICLE_HOST", "localhost")
CHRONICLE_PORT = int(os.getenv("CHRONICLE_PORT", "8001"))
CHRONICLE_IP = os.getenv("CHRONICLE_IP", "127.0.0.1")
CHRONICLE_BASE = os.getenv("CHRONICLE_BASE", "http://localhost:8001")
CHRONICLE_API_PATH = os.getenv("CHRONICLE_API_PATH", "/api")
CHRONICLE_API_URL = os.getenv("CHRONICLE_API_URL", f"{CHRONICLE_BASE}{CHRONICLE_API_PATH}")
CHRONICLE_DB_PATH = os.getenv("CHRONICLE_DB_PATH", str(Path.cwd() / "data" / "chronicle.db"))

# ZeroMQ addresses / tick settings
ZMQ_PUB_BIND_ADDR = os.getenv("ZMQ_PUB_BIND_ADDR", "tcp://127.0.0.1:5556")
ZMQ_PUB_CLIENT_ADDR = os.getenv("ZMQ_PUB_CLIENT_ADDR", "tcp://127.0.0.1:5557")
ZMQ_SUB_ADDR = os.getenv("ZMQ_SUB_ADDR", "tcp://127.0.0.1:5558")

TICK_PORT = int(os.getenv("TICK_PORT", "6000"))
USE_ZMQ_TICKS = os.getenv("USE_ZMQ_TICKS", "0") in ("1", "true", "True")
TICK_INTERVAL = float(os.getenv("TICK_INTERVAL", "1.0"))

# Tick publisher tuning
TICK_PUBLISHER_RECONNECT_DELAY = float(os.getenv("TICK_PUBLISHER_RECONNECT_DELAY", "0.5"))
TICK_PUBLISHER_MAX_QUEUE = int(os.getenv("TICK_PUBLISHER_MAX_QUEUE", "1000"))
TICK_PUBLISHER_DEAD_LETTER_FILE = os.getenv("TICK_PUBLISHER_DEAD_LETTER_FILE", "dead_letters.jsonl")
TICK_PUBLISHER_BACKPRESSURE_THRESHOLD = int(os.getenv("TICK_PUBLISHER_BACKPRESSURE_THRESHOLD", "800"))
TICK_PUBLISHER_BATCH_SIZE = int(os.getenv("TICK_PUBLISHER_BATCH_SIZE", "50"))
TICK_PUBLISHER_LAG_WARN_THRESHOLD = float(os.getenv("TICK_PUBLISHER_LAG_WARN_THRESHOLD", "0.5"))
TICK_PUBLISHER_MAX_RECONNECT_DELAY = float(os.getenv("TICK_PUBLISHER_MAX_RECONNECT_DELAY", "30.0"))

__all__ = [
    "CHRONICLE_HOST",
    "CHRONICLE_PORT",
    "CHRONICLE_IP",
    "CHRONICLE_BASE",
    "CHRONICLE_API_PATH",
    "CHRONICLE_API_URL",
    "CHRONICLE_DB_PATH",
    "ZMQ_PUB_BIND_ADDR",
    "ZMQ_PUB_CLIENT_ADDR",
    "ZMQ_SUB_ADDR",
    "TICK_PORT",
    "USE_ZMQ_TICKS",
    "TICK_INTERVAL",
    "TICK_PUBLISHER_RECONNECT_DELAY",
    "TICK_PUBLISHER_MAX_QUEUE",
    "TICK_PUBLISHER_DEAD_LETTER_FILE",
    "TICK_PUBLISHER_BACKPRESSURE_THRESHOLD",
    "TICK_PUBLISHER_BATCH_SIZE",
    "TICK_PUBLISHER_LAG_WARN_THRESHOLD",
    "TICK_PUBLISHER_MAX_RECONNECT_DELAY",
]
