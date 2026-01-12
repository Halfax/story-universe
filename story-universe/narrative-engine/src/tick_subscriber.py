"""ZMQ tick subscriber runner for the Narrative Engine.

Listens for `system_tick` messages from the Chronicle Keeper and triggers
the `NarrativeEngine` to generate and send events. Keeps imports and
initialization inside `main()` to avoid import-time side-effects.
"""
import time
import logging

def main():
    import zmq
    from src.config import ZMQ_SUB_ADDR
    from src.event_generator import NarrativeEngine

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("tick-subscriber")

    engine = NarrativeEngine(pi_base_url=None)  # uses default or CHRONICLE_BASE in config

    addr = ZMQ_SUB_ADDR
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    log.info("Connecting to tick publisher at %s", addr)
    sock.connect(addr)
    sock.setsockopt_string(zmq.SUBSCRIBE, "")

    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN)

    try:
        log.info("Tick subscriber started. Waiting for ticks...")
        while True:
            socks = dict(poller.poll(1000))
            if sock in socks and socks[sock] == zmq.POLLIN:
                msg = sock.recv_json()
                log.info("Received tick: %s", msg)
                # Only react to system_tick messages
                if msg.get("type") == "system_tick":
                    ev = engine.generate_event()
                    if ev:
                        sent = engine.send_event(ev)
                        log.info("Generated event %s sent=%s", ev.get("id"), sent)
            else:
                # periodic maintenance: advance arcs and save state
                engine._advance_arcs()
                time.sleep(0.05)
    except KeyboardInterrupt:
        log.info("Interrupted, shutting down")


if __name__ == "__main__":
    main()
