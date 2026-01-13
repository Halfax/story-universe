"""ZeroMQ publishers for Chronicle Keeper.

Provides a robust PUB socket wrapper for ticks and events with reconnection logic,
error handling, and metrics collection.
"""

import json
import time
import logging
import zmq
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any
from threading import Lock
import threading
import queue
from src.config import (
    ZMQ_PUB_CLIENT_ADDR,
    ZMQ_PUB_BIND_ADDR,
    TICK_PUBLISHER_RECONNECT_DELAY,
)

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class PublisherMetrics:
    """Metrics for message publishing."""

    messages_sent: int = 0
    message_errors: int = 0
    reconnects: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None
    last_success_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "messages_sent": self.messages_sent,
            "message_errors": self.message_errors,
            "reconnects": self.reconnects,
            "last_error": self.last_error,
            "last_error_time": self.last_error_time,
            "last_success_time": self.last_success_time,
            "uptime": (self.last_success_time or 0) - (self.last_error_time or 0),
        }


class ZmqPub:
    """Robust PUB socket wrapper with reconnection and metrics.

    Features:
    - Automatic reconnection on failure
    - Thread-safe publishing
    - Connection state tracking
    - Metrics collection
    - Graceful shutdown
    """

    def __init__(
        self, address: Optional[str] = None, bind: bool = True, topic_prefix: str = ""
    ):
        self.address = address or (ZMQ_PUB_BIND_ADDR if bind else ZMQ_PUB_CLIENT_ADDR)
        self.bind = bind
        self.topic_prefix = topic_prefix
        self._context: Optional[zmq.Context] = None
        self._socket: Optional[zmq.Socket] = None
        self._state = ConnectionState.DISCONNECTED
        self._lock = Lock()
        self.metrics = PublisherMetrics()
        self._shutdown = False
        self._reconnect_delay = TICK_PUBLISHER_RECONNECT_DELAY
        self._last_reconnect_attempt = 0.0
        # queueing/backpressure
        self._max_queue_size = 1000
        self._send_queue: "queue.Queue" = queue.Queue(maxsize=self._max_queue_size)
        self._sender_thread: Optional[threading.Thread] = None
        self._sender_shutdown = threading.Event()
        self._start_sender()
        # attempt connect after sender started
        self._connect()

    def _connect(self) -> bool:
        """Establish or re-establish the ZMQ connection."""
        with self._lock:
            if self._state == ConnectionState.CONNECTED:
                return True

            self._state = ConnectionState.CONNECTING

            try:
                # Clean up any existing socket
                if self._socket:
                    try:
                        self._socket.setsockopt(zmq.LINGER, 0)
                        self._socket.close()
                    except Exception as e:
                        logger.warning("Error closing existing socket: %s", e)

                # Create new socket
                self._context = zmq.Context.instance()
                self._socket = self._context.socket(zmq.PUB)
                self._socket.setsockopt(zmq.SNDHWM, 1000)
                self._socket.setsockopt(zmq.LINGER, 1000)

                if self.bind:
                    self._socket.bind(self.address)
                    # Allow subscribers to connect
                    time.sleep(0.1)
                else:
                    self._socket.connect(self.address)

                self._state = ConnectionState.CONNECTED
                self.metrics.reconnects += 1
                logger.info(
                    "Successfully %s to %s",
                    "bound" if self.bind else "connected",
                    self.address,
                )
                return True

            except Exception as e:
                error_msg = f"Failed to {'bind' if self.bind else 'connect to'} {self.address}: {str(e)}"
                logger.error(error_msg)
                self._state = ConnectionState.ERROR
                self.metrics.last_error = error_msg
                self.metrics.last_error_time = time.time()
                return False

    def _publish_impl(self, topic: str, payload: dict) -> bool:
        """Internal publish implementation with error handling and reconnection."""
        if self._shutdown:
            logger.warning("Publisher is shutting down, message not sent")
            return False

        if self._state != ConnectionState.CONNECTED:
            if not self._should_reconnect():
                return False
            if not self._connect():
                return False

        try:
            topic_frame = (self.topic_prefix + topic).encode("utf-8")
            json_frame = json.dumps(payload).encode("utf-8")
            self._socket.send_multipart([topic_frame, json_frame])

            # Update metrics on success
            self.metrics.messages_sent += 1
            self.metrics.last_success_time = time.time()
            return True

        except zmq.ZMQError as ze:
            error_msg = f"ZMQ error while publishing to {topic}: {str(ze)}"
            logger.error(error_msg)
            self._handle_publish_error(error_msg, ze)
            return False

        except Exception as e:
            error_msg = f"Unexpected error while publishing to {topic}: {str(e)}"
            logger.exception(error_msg)
            self._handle_publish_error(error_msg, e)
            return False

    def _should_reconnect(self) -> bool:
        """Determine if we should attempt to reconnect."""
        if self._shutdown:
            return False

        now = time.time()
        if now - self._last_reconnect_attempt < self._reconnect_delay:
            return False

        self._last_reconnect_attempt = now
        return True

    def _handle_publish_error(self, error_msg: str, exception: Exception):
        """Handle errors during publish and update state."""
        with self._lock:
            self.metrics.message_errors += 1
            self.metrics.last_error = error_msg
            self.metrics.last_error_time = time.time()
            self._state = ConnectionState.ERROR

            # Close the socket to ensure clean reconnection
            try:
                if self._socket:
                    self._socket.close(linger=0)
            except Exception as e:
                logger.warning("Error closing socket after error: %s", e)

    def publish(self, topic: str, payload: dict, max_retries: int = 2) -> bool:
        """Publish a JSON payload under `topic` using a bounded send queue.

        Args:
            topic: The topic to publish to
            payload: Dictionary payload to send (will be JSON-serialized)
            max_retries: Maximum number of retry attempts

        Returns:
            bool: True if message was successfully published, False otherwise
        """
        if self._shutdown:
            logger.warning("Publisher is shutting down, message not sent")
            return False

        try:
            # Non-blocking enqueue to avoid blocking producers under load.
            self._send_queue.put_nowait((topic, payload))
            return True
        except queue.Full:
            # Queue full -> count as an error/drop. Caller can retry if desired.
            self.metrics.message_errors += 1
            self.metrics.last_error = "send_queue_full"
            self.metrics.last_error_time = time.time()
            logger.warning("Send queue full, dropping message for topic %s", topic)
            return False

    def close(self):
        """Gracefully shut down the publisher."""
        # signal sender thread to stop
        self._sender_shutdown.set()
        if self._sender_thread and self._sender_thread.is_alive():
            self._sender_thread.join(timeout=2.0)

        with self._lock:
            self._shutdown = True
            try:
                if self._socket:
                    self._socket.setsockopt(zmq.LINGER, 100)
                    self._socket.close()
                # Avoid terminating the global ZMQ context instance here;
                # terminating can raise native errors in certain environments
                # if other sockets/contexts exist. Rely on socket close.
                try:
                    if (
                        self._context
                        and hasattr(self._context, "closed")
                        and not self._context.closed
                    ):
                        # best-effort: do not call term() on a shared context
                        pass
                except Exception:
                    pass
                self._state = ConnectionState.DISCONNECTED
                logger.info("Publisher closed successfully")
            except Exception as e:
                logger.exception("Error during publisher shutdown: %s", e)
            finally:
                self._socket = None
                self._context = None

    def _start_sender(self):
        """Start background sender thread which drains the send queue."""

        def loop():
            while not self._sender_shutdown.is_set():
                try:
                    topic, payload = self._send_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                try:
                    # attempt a best-effort send using existing impl
                    # if socket not connected, _publish_impl will attempt reconnect
                    # but protect with lock to avoid races.
                    with self._lock:
                        if self._state != ConnectionState.CONNECTED:
                            # attempt reconnect if allowed
                            if self._should_reconnect():
                                self._connect()
                        # if still not connected, re-enqueue or drop based on queue size
                        sent = False
                        try:
                            # directly send via socket to minimize overhead
                            if (
                                self._socket
                                and self._state == ConnectionState.CONNECTED
                            ):
                                topic_frame = (self.topic_prefix + topic).encode(
                                    "utf-8"
                                )
                                json_frame = json.dumps(payload).encode("utf-8")
                                self._socket.send_multipart([topic_frame, json_frame])
                                self.metrics.messages_sent += 1
                                self.metrics.last_success_time = time.time()
                                sent = True
                        except Exception:
                            # fallback to _publish_impl to trigger reconnection handling
                            try:
                                sent = self._publish_impl(topic, payload)
                            except Exception:
                                sent = False

                        if not sent:
                            # if we couldn't send, increment error and drop
                            self.metrics.message_errors += 1
                            self.metrics.last_error = "send_failed"
                            self.metrics.last_error_time = time.time()
                finally:
                    try:
                        self._send_queue.task_done()
                    except Exception:
                        pass

        self._sender_thread = threading.Thread(target=loop, daemon=True)
        self._sender_thread.start()


class LogPublisher(ZmqPub):
    def __init__(self, address=None, bind=False):
        super().__init__(address=address, bind=bind, topic_prefix="log:")

    def publish_log(self, log_data: dict):
        self.publish("entry", {"type": "log", **log_data})


class TickPublisher(ZmqPub):
    """Publisher for system ticks and events with additional metrics."""

    def __init__(self, address: Optional[str] = None, bind: bool = True):
        super().__init__(address=address, bind=bind, topic_prefix="system:")
        self._tick_count = 0
        self._start_time = time.time()

    def get_stats(self) -> Dict[str, Any]:
        """Get publisher statistics and metrics."""
        stats = {
            "tick_count": self._tick_count,
            "uptime": time.time() - self._start_time,
            "state": self._state.value,
            "metrics": self.metrics.to_dict(),
            "address": self.address,
            "bind_mode": self.bind,
            "topic_prefix": self.topic_prefix,
        }
        return stats

    def publish_tick(self, tick_data: dict, max_retries: int = 2) -> bool:
        """Publish a system tick with additional metadata.

        Args:
            tick_data: Dictionary containing tick data
            max_retries: Maximum number of retry attempts

        Returns:
            bool: True if tick was successfully published
        """
        self._tick_count += 1
        message = {
            "type": "system_tick",
            "tick_id": self._tick_count,
            "timestamp": time.time(),
            "data": tick_data,
        }
        return self.publish("tick", message, max_retries)

    def publish_event(self, event_data: dict, max_retries: int = 2) -> bool:
        """Publish an event with additional metadata.

        Args:
            event_data: Dictionary containing event data
            max_retries: Maximum number of retry attempts

        Returns:
            bool: True if event was successfully published
        """
        if not isinstance(event_data, dict):
            logger.error("Event data must be a dictionary")
            return False

        message = {
            "event_id": f"evt_{int(time.time() * 1000)}_{hash(frozenset(event_data.items()))}",
            "timestamp": time.time(),
            **event_data,
        }
        return self.publish("event", message, max_retries)


if __name__ == "__main__":
    # Enhanced CLI for testing the TickPublisher
    import argparse
    import signal
    import sys

    # json already imported at module level

    def print_stats(publisher: TickPublisher):
        """Print current publisher statistics."""
        stats = publisher.get_stats()
        print("\n=== Publisher Statistics ===")
        print(f"Status: {stats['state'].upper()}")
        print(f"Uptime: {stats['uptime']:.1f}s")
        print(f"Ticks published: {stats['tick_count']}")
        print(f"Messages sent: {stats['metrics']['messages_sent']}")
        print(f"Message errors: {stats['metrics']['message_errors']}")
        print(f"Reconnects: {stats['metrics']['reconnects']}")
        if stats["metrics"]["last_error"]:
            print(f"Last error: {stats['metrics']['last_error']}")
        print("=" * 30 + "\n")

    def signal_handler(sig, frame, publisher):
        print("\nShutting down publisher...")
        print_stats(publisher)
        publisher.close()
        sys.exit(0)

    def main():
        parser = argparse.ArgumentParser(description="Run a TickPublisher with metrics")
        parser.add_argument("--addr", help="ZMQ bind/conn address", default=None)
        parser.add_argument(
            "--bind", action="store_true", help="Bind instead of connect"
        )
        parser.add_argument(
            "--interval", type=float, default=1.0, help="Tick interval in seconds"
        )
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable debug logging"
        )
        args = parser.parse_args()

        # Configure logging
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler("publisher.log")],
        )

        logger.info("Starting TickPublisher (Ctrl+C to exit)")
        pub = TickPublisher(address=args.addr, bind=args.bind)

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, pub))

        try:
            counter = 0
            while True:
                counter += 1
                payload = {
                    "tick": counter,
                    "timestamp": time.time(),
                    "data": {"message": f"Test tick {counter}"},
                }

                success = pub.publish_tick(payload)
                if success:
                    logger.debug("Published tick %s", counter)
                else:
                    logger.warning("Failed to publish tick %s", counter)

                # Print stats every 10 ticks
                if counter % 10 == 0:
                    print_stats(pub)

                time.sleep(args.interval)

        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
        except Exception:
            logger.exception("Unexpected error:")
        finally:
            print("\nFinal statistics:")
            print_stats(pub)
            pub.close()
            logger.info("Publisher shut down successfully")

    if __name__ == "__main__":
        main()
