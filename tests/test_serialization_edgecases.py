import json
from models.canonical_event import CanonicalEvent


def test_canonical_event_roundtrip_minimal():
    payload = {
        'type': 'test.event',
        # intentionally omit optional fields like 'metadata' and 'id'
    }
    ev = CanonicalEvent(**payload)
    s = ev.json()
    d = json.loads(s)
    # id should be present after model validation (auto-generated)
    assert 'id' in d
    assert d['type'] == 'test.event'


def test_canonical_event_invalid_types_rejected():
    payload = {
        'id': 123,  # should be str
        'type': ['not', 'a', 'str']
    }
    try:
        CanonicalEvent(**payload)
        raised = False
    except Exception:
        raised = True
    assert raised
