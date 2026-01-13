import queue
from messaging.publisher import TickPublisher


def test_publisher_queue_behavior():
    pub = TickPublisher(address="tcp://127.0.0.1:5555", bind=False)
    # shrink the queue to force drops
    pub._send_queue = queue.Queue(maxsize=1)

    ok1 = pub.publish("tick", {"tick": 1})
    ok2 = pub.publish("tick", {"tick": 2})
    # first should enqueue, second should be dropped due to full queue
    assert ok1 is True
    assert ok2 is False or ok2 is not True
    pub.close()
