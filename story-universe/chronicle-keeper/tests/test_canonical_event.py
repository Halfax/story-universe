import time
import random
from src.models.canonical_event import CanonicalEvent


def test_canonical_event_basic():
    eid = f"evt_{int(time.time())}_{random.randint(0,9999)}"
    ev = CanonicalEvent(id=eid, type="character.move", timestamp=int(time.time()), source="test", data={"x":1}, metadata={})
    assert ev.id == eid
    assert ev.type == "character.move"
    assert isinstance(ev.timestamp, int)
