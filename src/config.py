"""Narrative-engine package configuration.

Re-exports authoritative configuration constants from `shared.config`.
Edit `shared/config.py` to change defaults; no os.getenv calls are used here.
"""

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
)

# Runtime toggles (centralized in shared.config)
from shared.config import USE_ZMQ_TICKS, TICK_INTERVAL
from shared.config import (
    TICK_PUBLISHER_RECONNECT_DELAY,
    TICK_PUBLISHER_MAX_QUEUE,
    TICK_PUBLISHER_DEAD_LETTER_FILE,
    TICK_PUBLISHER_BACKPRESSURE_THRESHOLD,
    TICK_PUBLISHER_BATCH_SIZE,
    TICK_PUBLISHER_LAG_WARN_THRESHOLD,
    TICK_PUBLISHER_MAX_RECONNECT_DELAY,
)
