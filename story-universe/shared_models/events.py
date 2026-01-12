from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class EventType(str, Enum):
    # System events
    SYSTEM_STARTUP = "system:startup"
    SYSTEM_SHUTDOWN = "system:shutdown"
    SYSTEM_TICK = "system:tick"
    SYSTEM_ERROR = "system:error"
    
    # World events
    ENTITY_CREATED = "world:entity:created"
    ENTITY_UPDATED = "world:entity:updated"
    ENTITY_DELETED = "world:entity:deleted"
    ENTITY_MOVED = "world:entity:moved"
    
    # Character events
    CHARACTER_CREATED = "character:created"
    CHARACTER_UPDATED = "character:updated"
    CHARACTER_DELETED = "character:deleted"
    CHARACTER_LEVEL_UP = "character:level_up"
    CHARACTER_DAMAGED = "character:damaged"
    CHARACTER_HEALED = "character:healed"
    
    # Item events
    ITEM_CREATED = "item:created"
    ITEM_UPDATED = "item:updated"
    ITEM_DELETED = "item:deleted"
    ITEM_ACQUIRED = "item:acquired"
    ITEM_LOST = "item:lost"
    ITEM_USED = "item:used"
    
    # Location events
    LOCATION_DISCOVERED = "location:discovered"
    LOCATION_UPDATED = "location:updated"
    
    # Quest events
    QUEST_STARTED = "quest:started"
    QUEST_UPDATED = "quest:updated"
    QUEST_COMPLETED = "quest:completed"
    QUEST_FAILED = "quest:failed"
    
    # Combat events
    COMBAT_STARTED = "combat:started"
    COMBAT_ENDED = "combat:ended"
    COMBAT_TURN = "combat:turn"
    
    # Dialogue events
    DIALOGUE_STARTED = "dialogue:started"
    DIALOGUE_CHOICE = "dialogue:choice"
    DIALOGUE_ENDED = "dialogue:ended"

class EventMetadata(BaseModel):
    """Metadata for an event."""
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_id: Optional[UUID] = Field(None, description="ID of the event source")
    correlation_id: Optional[UUID] = Field(None, description="For grouping related events")
    version: str = Field("1.0.0", description="Event schema version")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }

class BaseEvent(BaseModel):
    """Base class for all events."""
    type: EventType
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: EventMetadata = Field(default_factory=EventMetadata)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }

class SystemEvent(BaseEvent):
    """System-level events."""
    type: EventType = Field(..., description="Type of system event")
    
    @validator('type')
    def validate_type(cls, v):
        if not v.value.startswith('system:'):
            raise ValueError("System event type must start with 'system:'")
        return v

class WorldEvent(BaseEvent):
    """World state change events."""
    type: EventType = Field(..., description="Type of world event")
    entity_type: str = Field(..., description="Type of entity affected")
    entity_id: UUID = Field(..., description="ID of the affected entity")
    
    @validator('type')
    def validate_type(cls, v):
        if not v.value.startswith('world:'):
            raise ValueError("World event type must start with 'world:'")
        return v

class NarrativeEvent(BaseEvent):
    """Narrative and gameplay events."""
    type: EventType = Field(..., description="Type of narrative event")
    character_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of characters involved"
    )
    location_id: Optional[UUID] = Field(
        None,
        description="ID of the location where this occurred"
    )
    
    @validator('type')
    def validate_type(cls, v):
        if v.value.startswith(('system:', 'world:')):
            raise ValueError("Narrative event type cannot be a system or world event")
        return v

# Type alias for any event type
Event = Union[SystemEvent, WorldEvent, NarrativeEvent]

# Example event constructors
def create_system_tick(tick_data: Dict[str, Any]) -> SystemEvent:
    """Create a system tick event."""
    return SystemEvent(
        type=EventType.SYSTEM_TICK,
        data={
            "tick_data": tick_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

def create_entity_updated(
    entity_type: str,
    entity_id: UUID,
    changes: Dict[str, Any],
    source_id: Optional[UUID] = None
) -> WorldEvent:
    """Create an entity updated event."""
    return WorldEvent(
        type=EventType.ENTITY_UPDATED,
        entity_type=entity_type,
        entity_id=entity_id,
        data={"changes": changes},
        metadata=EventMetadata(source_id=source_id)
    )

def create_quest_completed(
    quest_id: UUID,
    character_id: UUID,
    rewards: Dict[str, Any],
    source_id: Optional[UUID] = None
) -> NarrativeEvent:
    """Create a quest completed event."""
    return NarrativeEvent(
        type=EventType.QUEST_COMPLETED,
        character_ids=[character_id],
        data={
            "quest_id": str(quest_id),
            "rewards": rewards
        },
        metadata=EventMetadata(source_id=source_id)
    )
