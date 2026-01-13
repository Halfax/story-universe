import time
import zmq

from src.messaging.publisher import TickPublisher, ConnectionState


class _MockSocketFailOnce:
    def __init__(self):
        self._failed = False

    def send_multipart(self, frames):
        if not self._failed:
            self._failed = True
            raise zmq.ZMQError("simulated send failure")
        # succeed on subsequent calls
        return True

    def close(self, *args, **kwargs):
        pass


def test_publish_retries_and_recovers():
    pub = TickPublisher(bind=False)
    # force a connected state and inject a mock socket that fails once
    pub._state = ConnectionState.CONNECTED
    pub._socket = _MockSocketFailOnce()

    # first publish should trigger internal error handling and return False
    ok1 = pub._publish_impl("tick", {"tick": 1})
    assert ok1 is False
    assert pub.metrics.message_errors >= 1
    assert pub._state == ConnectionState.ERROR or pub.metrics.message_errors >= 1

    # simulate recovery: reset state and set a healthy socket
    pub._state = ConnectionState.CONNECTED
    ok2 = pub._publish_impl("tick", {"tick": 2})
    assert ok2 is True

    pub.close()
