from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from .base import Entity

class CharacterStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"
    MISSING = "missing"
    UNKNOWN = "unknown"

class CharacterStats(BaseModel):
    """Character attributes and statistics."""
    strength: int = Field(5, ge=1, le=20, description="Physical power")
    dexterity: int = Field(5, ge=1, le=20, description="Agility and reflexes")
    constitution: int = Field(5, ge=1, le=20, description="Endurance and health")
    intelligence: int = Field(5, ge=1, le=20, description="Mental acuity")
    wisdom: int = Field(5, ge=1, le=20, description="Perception and insight")
    charisma: int = Field(5, ge=1, le=20, description="Force of personality")
    
    class Config:
        schema_extra = {
            "example": {
                "strength": 10,
                "dexterity": 8,
                "constitution": 12,
                "intelligence": 14,
                "wisdom": 13,
                "charisma": 16
            }
        }

class RelationshipType(str, Enum):
    FRIEND = "friend"
    FAMILY = "family"
    ROMANTIC = "romantic"
    RIVAL = "rival"
    ENEMY = "enemy"
    NEUTRAL = "neutral"

class CharacterRelationship(BaseModel):
    """Relationship between two characters."""
    target_id: str = Field(..., description="ID of the related character")
    type: RelationshipType = Field(..., description="Type of relationship")
    strength: float = Field(0.0, ge=-1.0, le=1.0, description="Relationship strength")
    description: str = Field("", description="Description of the relationship")
    
    class Config:
        schema_extra = {
            "example": {
                "target_id": "char-456",
                "type": "friend",
                "strength": 0.8,
                "description": "Childhood friends"
            }
        }

class Character(Entity):
    """A character in the world."""
    type: str = Field("character", const=True)
    status: CharacterStatus = Field(CharacterStatus.ACTIVE)
    species: str = Field("human", description="Species or race")
    age: Optional[int] = Field(None, ge=0, description="Age in years")
    gender: Optional[str] = Field(None, description="Gender identity")
    current_location: Optional[str] = Field(
        None, 
        description="ID of current location"
    )
    inventory: List[str] = Field(
        default_factory=list, 
        description="List of item IDs in inventory"
    )
    stats: CharacterStats = Field(default_factory=CharacterStats)
    relationships: Dict[str, CharacterRelationship] = Field(
        default_factory=dict,
        description="Relationships with other characters"
    )
    
    class Config(Entity.Config):
        schema_extra = {
            **Entity.Config.schema_extra["example"],
            "type": "character",
            "status": "active",
            "species": "human",
            "age": 32,
            "gender": "non-binary",
            "current_location": "loc-123",
            "inventory": ["item-1", "item-2"],
            "stats": CharacterStats.Config.schema_extra["example"],
            "relationships": {
                "char-456": CharacterRelationship.Config.schema_extra["example"]
            }
        }
