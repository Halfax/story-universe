"""
World Clock and Tick Broadcasting for Chronicle Keeper
-----------------------------------------------------
Maintains canonical world time, advances it on a schedule, logs ticks,
and broadcasts to subscribers with enhanced reliability and metrics.
"""

import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from src.db.database import get_connection
from src.messaging.publisher import TickPublisher, ConnectionState
from src.config import TICK_PUBLISHER_RECONNECT_DELAY

logger = logging.getLogger(__name__)


import json


class WorldClock:
    """Manages the world clock and tick broadcasting."""

    def __init__(self, tick_interval: float = 5.0, db_path: Optional[str] = None):
        """Initialize the world clock.

        Args:
            tick_interval: Time in seconds between ticks
        """
        self.tick_interval = tick_interval
        # optional db_path is accepted for test compatibility; not required
        self.db_path = db_path
        # Avoid binding by default in test environments; use client connect mode
        self.publisher = TickPublisher(bind=False)
        self._shutdown = threading.Event()
        self._thread: Optional[threading.Thread] = None
        # Public test-friendly running flag and internal shorthand
        self._running = False
        self.metrics = {
            "ticks_processed": 0,
            "tick_errors": 0,
            "last_tick_time": None,
            "start_time": time.time(),
            "last_error": None,
        }

    def _process_tick(self) -> bool:
        """Process a single tick of the world clock.

        Returns:
            bool: True if the tick was processed successfully
        """
        try:
            with get_connection() as conn:
                c = conn.cursor()

                # Get current time from system_state
                c.execute("SELECT value FROM system_state WHERE key='time'")
                row = c.fetchone()
                current_time = int(row[0]) if row else 0
                new_time = current_time + 1

                # Update time in database
                c.execute(
                    "REPLACE INTO system_state (key, value) VALUES (?, ?)",
                    ("time", str(new_time)),
                )

                # Log tick event
                tick_data = {
                    "world_time": new_time,
                    "previous_time": current_time,
                    "tick_duration": self.tick_interval,
                    "system_time": datetime.utcnow().isoformat(),
                }

                c.execute(
                    """
                    INSERT INTO events (
                        timestamp, 
                        type, 
                        description, 
                        involved_characters, 
                        involved_locations, 
                        metadata
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        int(time.time()),
                        "system_tick",
                        f"World time advanced to {new_time}",
                        "[]",
                        "[]",
                        json.dumps(tick_data),
                    ),
                )

                conn.commit()

                # Broadcast tick to subscribers
                success = False
                try:
                    success = self.publisher.publish_tick(tick_data)
                except Exception:
                    # best-effort publish; do not fail tick on publish error
                    success = False
                if not success:
                    logger.warning("Failed to publish tick %s", new_time)

                # Update metrics
                self.metrics["ticks_processed"] += 1
                self.metrics["last_tick_time"] = time.time()

                if self.metrics["ticks_processed"] % 10 == 0:
                    self._log_metrics()

                return True

        except Exception as e:
            error_msg = f"Error processing tick: {str(e)}"
            logger.exception(error_msg)
            self.metrics["tick_errors"] += 1
            self.metrics["last_error"] = error_msg
            return False

    def _log_metrics(self):
        """Log current metrics."""
        uptime = time.time() - self.metrics["start_time"]
        ticks_per_second = self.metrics["ticks_processed"] / uptime if uptime > 0 else 0

        logger.info(
            "Clock metrics: ticks=%d, errors=%d, tps=%.2f, uptime=%.1fs",
            self.metrics["ticks_processed"],
            self.metrics["tick_errors"],
            ticks_per_second,
            uptime,
        )

        # Log publisher stats if available
        try:
            pub_stats = self.publisher.get_stats()
            logger.debug(
                "Publisher stats: state=%s, sent=%d, errors=%d, reconnects=%d",
                pub_stats["state"].upper(),
                pub_stats["metrics"]["messages_sent"],
                pub_stats["metrics"]["message_errors"],
                pub_stats["metrics"]["reconnects"],
            )
        except Exception as e:
            logger.warning("Could not get publisher stats: %s", str(e))

    def _run_loop(self):
        """Main clock loop."""
        logger.info("Starting world clock loop (interval=%.1fs)", self.tick_interval)

        while not self._shutdown.is_set():
            start_time = time.time()

            if not self._process_tick():
                # On error, wait a bit before retrying
                time.sleep(min(1.0, self.tick_interval))

            # Sleep for remaining time in the tick interval
            elapsed = time.time() - start_time
            sleep_time = max(0, self.tick_interval - elapsed)
            if sleep_time > 0:
                self._shutdown.wait(sleep_time)

        logger.info("World clock loop stopped")

    def start(self):
        """Start the world clock in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("World clock is already running")
            return False

        self._shutdown.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._running = True
        logger.info("World clock started")
        return True

    def stop(self):
        """Stop the world clock."""
        self._shutdown.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.tick_interval * 2)

        # Close the publisher
        try:
            self.publisher.close()
        except Exception as e:
            logger.exception("Error closing publisher: %s", e)

        logger.info("World clock stopped")
        self._running = False

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the world clock."""
        return {
            "running": self._thread.is_alive() if self._thread else False,
            "tick_interval": self.tick_interval,
            "metrics": self.metrics.copy(),
            "publisher_status": (
                self.publisher.get_stats() if hasattr(self, "publisher") else {}
            ),
        }

    def _write_tick(self, tick_data: Dict[str, Any]) -> None:
        """Write tick metadata safely. Try DB insert first, fallback to file next-to-db path."""
        try:
            conn = get_connection()
            c = conn.cursor()
            import json as _json

            c.execute(
                """
                INSERT INTO events (timestamp, type, description, involved_characters, involved_locations, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    int(time.time()),
                    "system_tick",
                    f"tick {tick_data.get('tick')}",
                    "[]",
                    "[]",
                    _json.dumps(tick_data),
                ),
            )
            conn.commit()
            try:
                conn.close()
            except Exception:
                pass
            return
        except Exception:
            # fallback: write a small metadata file near db_path if available
            try:
                if self.db_path:
                    from pathlib import Path

                    p = Path(self.db_path).with_suffix(".tickmeta")
                    import json as _json2

                    with open(p, "a", encoding="utf-8") as f:
                        f.write(_json2.dumps(tick_data) + "\n")
            except Exception:
                pass
            return


# Global instance for backward compatibility
_world_clock = WorldClock()


def start_world_clock(tick_interval: float = 5.0) -> bool:
    """Start the world clock (for backward compatibility).

    Args:
        tick_interval: Time in seconds between ticks

    Returns:
        bool: True if the clock started successfully
    """
    global _world_clock
    _world_clock = WorldClock(tick_interval)
    return _world_clock.start()


def stop_world_clock():
    """Stop the world clock (for backward compatibility)."""
    global _world_clock
    _world_clock.stop()


def get_clock_status() -> Dict[str, Any]:
    """Get the status of the world clock (for backward compatibility)."""
    global _world_clock
    return _world_clock.get_status() if hasattr(_world_clock, "get_status") else {}
