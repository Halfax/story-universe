from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator
from .base import Entity

class LocationType(str, Enum):
    SETTLEMENT = "settlement"
    BUILDING = "building"
    LANDMARK = "landmark"
    REGION = "region"
    DUNGEON = "dungeon"
    OTHER = "other"

class Coordinates(BaseModel):
    """Geographic coordinates."""
    x: float = Field(0.0, description="X coordinate")
    y: float = Field(0.0, description="Y coordinate")
    z: float = Field(0.0, description="Z coordinate or elevation")
    
    class Config:
        schema_extra = {
            "example": {
                "x": 42.5,
                "y": -12.3,
                "z": 0.0
            }
        }

class Connection(BaseModel):
    """Connection between two locations."""
    target_id: str = Field(..., description="ID of connected location")
    direction: Optional[str] = Field(
        None, 
        description="Direction or relative position (e.g., 'north', 'upstairs')"
    )
    distance: float = Field(1.0, ge=0, description="Distance in arbitrary units")
    is_bidirectional: bool = Field(True, description="Can travel both ways")
    
    class Config:
        schema_extra = {
            "example": {
                "target_id": "loc-456",
                "direction": "north",
                "distance": 1.5,
                "is_bidirectional": True
            }
        }

class PointOfInterest(BaseModel):
    """Notable feature within a location."""
    name: str = Field(..., max_length=100)
    description: str = Field("")
    position: Optional[Coordinates] = None
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Ancient Fountain",
                "description": "A weathered stone fountain with faintly glowing runes.",
                "position": {"x": 5.2, "y": 3.1, "z": 0.0},
                "tags": ["magical", "ancient"]
            }
        }

class Location(Entity):
    """A location in the world."""
    type: str = Field("location", const=True)
    location_type: LocationType = Field(LocationType.OTHER)
    parent_location: Optional[str] = Field(
        None, 
        description="ID of containing location"
    )
    coordinates: Optional[Coordinates] = Field(
        None,
        description="Geographic position"
    )
    connections: Dict[str, Connection] = Field(
        default_factory=dict,
        description="Connections to other locations"
    )
    points_of_interest: List[PointOfInterest] = Field(
        default_factory=list,
        description="Notable features within this location"
    )
    is_accessible: bool = Field(
        True, 
        description="Can characters enter this location?"
    )
    
    @validator('connections')
    def check_self_reference(cls, v, values):
        if 'id' in values and values['id'] in v:
            raise ValueError("Location cannot connect to itself")
        return v
    
    class Config(Entity.Config):
        schema_extra = {
            **Entity.Config.schema_extra["example"],
            "type": "location",
            "location_type": "settlement",
            "parent_location": "region-123",
            "coordinates": {"x": 42.5, "y": -12.3, "z": 0.0},
            "connections": {
                "loc-456": Connection.Config.schema_extra["example"]
            },
            "points_of_interest": [
                PointOfInterest.Config.schema_extra["example"]
            ],
            "is_accessible": True
        }
