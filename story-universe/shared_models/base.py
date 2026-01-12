import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, UUID4

class EntityType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    ITEM = "item"
    EVENT = "event"

class Entity(BaseModel):
    """Base class for all entities in the world."""
    id: UUID4 = Field(default_factory=uuid4, description="Unique identifier")
    type: EntityType = Field(..., description="Type of entity")
    name: str = Field(..., max_length=100, description="Display name")
    description: str = Field(default="", description="Detailed description")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional metadata"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, ge=1)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "character",
                "name": "Example Entity",
                "description": "An example entity",
                "tags": ["example", "test"],
                "metadata": {},
                "created_at": "2023-01-12T12:00:00Z",
                "updated_at": "2023-01-12T12:00:00Z",
                "version": 1
            }
        }

class Event(BaseModel):
    """Base class for all events."""
    id: UUID4 = Field(default_factory=uuid4)
    type: str = Field(..., description="Event type identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[UUID4] = Field(None, description="Source entity ID")
    target: Optional[UUID4] = Field(None, description="Target entity ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional metadata"
    )

class WorldState(BaseModel):
    """Represents the state of the world at a point in time."""
    current_time: int = Field(0, ge=0, description="Current world time in ticks")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field("0.1.0", description="World state version")
    
    class Config:
        schema_extra = {
            "example": {
                "current_time": 42,
                "last_updated": "2023-01-12T12:00:00Z",
                "version": "0.1.0"
            }
        }
