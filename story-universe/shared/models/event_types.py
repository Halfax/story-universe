# Canonical Event Types for the Story Universe
from enum import Enum

class EventType(str, Enum):
    CHARACTER_ACTION = "character_action"
    WORLD_EVENT = "world_event"
    FACTION_EVENT = "faction_event"
    ENVIRONMENT_CHANGE = "environment_change"
    SYSTEM_TICK = "system_tick"

# Example Pydantic model for a canonical event
from pydantic import BaseModel
from typing import List, Dict, Any

class CanonicalEvent(BaseModel):
    id: int
    type: EventType
    timestamp: int
    description: str
    involved_characters: List[int] = []
    involved_locations: List[int] = []
    metadata: Dict[str, Any] = {}
