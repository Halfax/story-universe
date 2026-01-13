from services.continuity import ContinuityValidator


def test_continuity_dead_cannot_act():
    # provided world state with a dead character
    ws = {"characters": {"1": {"name": "Bob", "status": "dead"}}, "locations": {}, "factions": {}, "recent_events": []}
    v = ContinuityValidator(world_state=ws)
    event = {"type": "character_action", "character_id": "1", "action": "attack", "timestamp": 100}
    ok, reason = v.validate_event(event)
    assert not ok
    assert "dead" in reason.lower()


def test_continuity_identity_conflict():
    ws = {"characters": {"1": {"name": "Alice", "status": "alive"}}, "locations": {}, "factions": {}, "recent_events": []}
    v = ContinuityValidator(world_state=ws)
    # trying to create another character with same name
    event = {"type": "character_create", "name": "Alice", "character_id": "2"}
    ok, reason = v.validate_event(event)
    assert not ok
    assert "identity" in reason.lower()
def test_relationship_to_self():
    # Both source and target must be alive for the self-relationship constraint to trigger
    world = make_world_state()
    world["characters"]["1"]["status"] = "alive"
    v = ContinuityValidator(world)
    event = {"type": "relationship_change", "source_id": "1", "target_id": "1", "relationship_type": "ally"}
    valid, reason = v.validate_event(event)
    assert not valid and "self" in reason

def test_forbidden_relationship_type():
    # Add a third alive character to test forbidden relationship type
    world = make_world_state()
    world["characters"]["3"] = {"name": "Charlie", "status": "alive"}
    v = ContinuityValidator(world)
    event = {"type": "relationship_change", "source_id": "1", "target_id": "3", "relationship_type": "archenemy"}
    valid, reason = v.validate_event(event)
    assert not valid and "forbidden" in reason
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.continuity import ContinuityValidator

def make_world_state():
    """
    Returns a sample world state for testing.
    Characters:
      1: Alice (alive)
      2: Bob (dead)
    """
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
        "recent_events": [
            {"id": 42},
            {"character_id": "1", "timestamp": 1100},
            {"location_id": "100", "timestamp": 1200}
        ]
    }
def test_invalid_state_transition_dead_to_alive():
    v = ContinuityValidator(make_world_state())
    # Bob is dead, cannot transition to alive
    event = {"type": "character_state_change", "character_id": "2", "new_status": "alive"}
    valid, reason = v.validate_event(event)
    assert not valid and "Invalid character state transition" in reason

def test_valid_state_transition_alive_to_dead():
    v = ContinuityValidator(make_world_state())
    # Alice is alive, can transition to dead
    event = {"type": "character_state_change", "character_id": "1", "new_status": "dead"}
    valid, reason = v.validate_event(event)
    assert valid

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
    event = {"type": "character_action", "character_id": "1", "location_id": "100", "timestamp": 1300}
    valid, reason = v.validate_event(event)
    assert valid

def test_timeline_inconsistency_character():
    v = ContinuityValidator(make_world_state())
    # Retroactive event for character 1 (existing event at 1100)
    event = {"type": "character_action", "character_id": "1", "timestamp": 1050}
    valid, reason = v.validate_event(event)
    assert not valid and "retroactive" in reason

def test_timeline_inconsistency_location():
    v = ContinuityValidator(make_world_state())
    # Retroactive event for location 100 (existing event at 1200)
    event = {"type": "character_action", "location_id": "100", "timestamp": 1100}
    valid, reason = v.validate_event(event)
    assert not valid and "retroactive" in reason

def test_faction_alliance_with_enemy():
    world = make_world_state()
    # Set 10 and 20 as enemies
    world["factions"]["10"]["relationships"]["20"] = "enemy"
    world["factions"]["20"]["relationships"]["10"] = "enemy"
    v = ContinuityValidator(world)
    event = {"type": "faction_event", "source_faction_id": "10", "target_faction_id": "20", "action": "form_alliance"}
    valid, reason = v.validate_event(event)
    assert not valid and "enemy" in reason

def test_faction_betrayal_without_rivalry():
    world = make_world_state()
    # 10 and 20 are allies, but not rivals
    v = ContinuityValidator(world)
    event = {"type": "faction_event", "source_faction_id": "10", "target_faction_id": "20", "action": "betray"}
    valid, reason = v.validate_event(event)
    assert not valid and "rivalry" in reason

def test_faction_betrayal_with_rivalry():
    world = make_world_state()
    # 10 and 20 are allies, but 20 considers 10 a rival
    world["factions"]["20"]["relationships"]["10"] = "rival"
    v = ContinuityValidator(world)
    event = {"type": "faction_event", "source_faction_id": "10", "target_faction_id": "20", "action": "betray"}
    valid, reason = v.validate_event(event)
    assert valid

def test_move_to_nonexistent_location():
    world = make_world_state()
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "move", "location_id": "999"}
    valid, reason = v.validate_event(event)
    assert not valid and "does not exist" in reason

def test_move_to_forbidden_location():
    world = make_world_state()
    world["locations"]["200"]["forbidden"] = True
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "move", "location_id": "200"}
    valid, reason = v.validate_event(event)
    assert not valid and "forbidden" in reason

def test_move_to_locked_location():
    world = make_world_state()
    world["locations"]["100"]["locked"] = True
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "move", "location_id": "100"}
    valid, reason = v.validate_event(event)
    assert not valid and "locked" in reason

def test_dead_character_cannot_act():
    world = make_world_state()
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "2", "action": "move", "location_id": "100"}
    valid, reason = v.validate_event(event)
    assert not valid and ("dead" in reason or "cannot act" in reason)

def test_dead_character_cannot_change_state():
    world = make_world_state()
    v = ContinuityValidator(world)
    event = {"type": "character_state_change", "character_id": "2", "new_status": "missing"}
    valid, reason = v.validate_event(event)
    assert not valid and ("Invalid character state transition" in reason or "dead" in reason)

def test_cannot_resurrect_dead_character():
    world = make_world_state()
    v = ContinuityValidator(world)
    event = {"type": "character_state_change", "character_id": "2", "new_status": "alive"}
    valid, reason = v.validate_event(event)
    assert not valid and ("Invalid character state transition" in reason or "resurrect" in reason)

def test_impossible_state_change():
    world = make_world_state()
    v = ContinuityValidator(world)
    event = {"type": "character_state_change", "character_id": "1", "new_status": "alive"}
    valid, reason = v.validate_event(event)
    assert not valid and ("Invalid character state transition" in reason or "already alive" in reason)

def test_magic_cast_without_trait():
    world = make_world_state()
    # Alice has no magic trait
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "cast_spell"}
    valid, reason = v.validate_event(event)
    assert not valid and "cannot cast spells" in reason

def test_magic_cast_with_trait():
    world = make_world_state()
    world["characters"]["1"]["traits"] = ["magic"]
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "cast_spell"}
    valid, reason = v.validate_event(event)
    assert valid

def test_fly_without_trait():
    world = make_world_state()
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "fly"}
    valid, reason = v.validate_event(event)
    assert not valid and "cannot fly" in reason

def test_fly_with_trait():
    world = make_world_state()
    world["characters"]["1"]["traits"] = ["fly"]
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "fly"}
    valid, reason = v.validate_event(event)
    assert valid

def test_enter_forbidden_region():
    world = make_world_state()
    world["locations"]["100"]["political_status"] = "forbidden"
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "enter_region", "location_id": "100"}
    valid, reason = v.validate_event(event)
    assert not valid and "politically forbidden" in reason

def test_attack_protected_character():
    world = make_world_state()
    world["characters"]["2"]["protected"] = True
    v = ContinuityValidator(world)
    event = {"type": "character_action", "character_id": "1", "action": "attack", "target_id": "2"}
    valid, reason = v.validate_event(event)
    assert not valid and "protected character" in reason
