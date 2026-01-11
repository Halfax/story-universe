import pytest
from src.services.continuity import ContinuityValidator

def make_world_state():
    return {
        "characters": {
            "1": {"name": "Alice", "status": "alive"},
            "2": {"name": "Bob", "status": "dead"}
        },
        "locations": {
            "100": {"name": "Town"},
            "200": {"name": "Forest"}
        },
        "factions": {
            "10": {"relationships": {"20": "ally"}},
            "20": {"relationships": {"10": "ally"}}
        },
        "time": 1000,
        "recent_events": [{"id": 42}]
    }

def test_missing_type():
    v = ContinuityValidator(make_world_state())
    valid, reason = v.validate_event({"character_id": "1"})
    assert not valid and "type missing" in reason

def test_dead_character():
    v = ContinuityValidator(make_world_state())
    valid, reason = v.validate_event({"type": "action", "character_id": "2"})
    assert not valid and "dead" in reason

def test_duplicate_event():
    v = ContinuityValidator(make_world_state())
    valid, reason = v.validate_event({"type": "character_action", "id": 42})
    assert not valid and "Duplicate" in reason

def test_faction_attack_ally():
    v = ContinuityValidator(make_world_state())
    event = {"type": "faction_event", "source_faction_id": "10", "target_faction_id": "20", "action": "attack"}
    valid, reason = v.validate_event(event)
    assert not valid and "ally" in reason

def test_valid_event():
    v = ContinuityValidator(make_world_state())
    event = {"type": "character_action", "character_id": "1", "location_id": "100", "timestamp": 1001}
    valid, reason = v.validate_event(event)
    assert valid
