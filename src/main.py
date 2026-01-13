"""Narrative Engine runner.

Runs the `NarrativeEngine` from `event_generator.py` either on a simple interval
or triggered by ZeroMQ ticks from the Chronicle Keeper.

Usage:
    python -m src.main

Environment variables:
    CHRONICLE_BASE_URL - base URL for the Chronicle Keeper (default http://127.0.0.1:8001)
    USE_ZMQ_TICKS - if set to '1', try to subscribe to Pi ticks via ZeroMQ
    TICK_INTERVAL - fallback interval in seconds when not using ZMQ (default 5)
"""
import time
import logging

from event_generator import NarrativeEngine
from config import (
    CHRONICLE_BASE,
    USE_ZMQ_TICKS,
    TICK_INTERVAL,
    ZMQ_PUB_CLIENT_ADDR,
)


LOG = logging.getLogger("narrative-engine")
logging.basicConfig(level=logging.INFO)


def run_interval_mode(engine: NarrativeEngine, interval: int = 5):
    LOG.info("Starting interval mode: generating every %ds", interval)
    try:
        while True:
            ev = engine.generate_event()
            if ev:
                sent = engine.send_event(ev)
                LOG.info("Generated event %s sent=%s", ev.get("id"), sent)
            time.sleep(interval)
    except KeyboardInterrupt:
        LOG.info("Interrupted, exiting")


def run_zmq_mode(engine: NarrativeEngine, zmq_addr: str):
    try:
        import zmq
    except Exception:
        LOG.error("pyzmq not available, cannot run ZMQ mode")
        return

    LOG.info("Starting ZMQ mode, subscribing to %s", zmq_addr)
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.connect(zmq_addr)
    sock.setsockopt_string(zmq.SUBSCRIBE, "")

    try:
        while True:
            msg = sock.recv_json()
            # Expected tick message; we generate one event per tick
            LOG.info("Received tick: %s", msg)
            ev = engine.generate_event()
            if ev:
                sent = engine.send_event(ev)
                LOG.info("Generated event %s sent=%s", ev.get("id"), sent)
    except KeyboardInterrupt:
        LOG.info("Interrupted, exiting ZMQ loop")


def main():
    engine = NarrativeEngine(pi_base_url=CHRONICLE_BASE)

    if USE_ZMQ_TICKS:
        run_zmq_mode(engine, ZMQ_PUB_CLIENT_ADDR)
    else:
        run_interval_mode(engine, TICK_INTERVAL)


if __name__ == "__main__":
    main()
