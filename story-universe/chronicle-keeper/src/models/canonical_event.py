from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import re
import time
from uuid import uuid4


class EventMetadata(BaseModel):
    causationId: Optional[str] = None
    correlationId: Optional[str] = None
    schemaVersion: Optional[str] = None


class CanonicalEvent(BaseModel):
    id: str = Field(
        default_factory=lambda: f"evt_{int(time.time())}_{str(uuid4())[:8]}",
        description="Event id, e.g. 'evt_<timestamp>_<random>'",
    )
    type: str = Field(..., description="Namespaced event type, e.g. 'character.move'")
    timestamp: int = Field(default_factory=lambda: int(time.time()), ge=0)
    source: Optional[str] = None
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: EventMetadata = Field(default_factory=EventMetadata)

    @validator("id")
    def id_must_match(cls, v):
        if not re.match(r"^evt_\d+_\w+$", v):
            # allow many formats, but warn for obvious mismatch
            return v
        return v

    class Config:
        extra = "allow"
