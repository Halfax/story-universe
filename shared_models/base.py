"""Base classes for all models and events."""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar
from uuid import UUID, uuid4

T = TypeVar('T', bound='Model')


class Serializable(ABC):
    """Interface for serializable objects."""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create object from dictionary."""
        pass


class Model(Serializable):
    """Base class for all domain models."""
    
    def __init__(self, id: Optional[UUID] = None, **kwargs):
        self.id = id or uuid4()
        self.created_at = kwargs.get('created_at') or datetime.utcnow()
        self.updated_at = kwargs.get('updated_at') or self.created_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            **self._serialize()
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model from dictionary."""
        return cls(**data)
    
    def _serialize(self) -> Dict[str, Any]:
        """Override in subclasses to add model-specific fields."""
        return {}


class Event(Serializable):
    """Base class for all events."""
    
    def __init__(
        self,
        event_type: str,
        source: str,
        data: Dict[str, Any],
        causation_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        self.id = event_id or f"evt_{int(datetime.utcnow().timestamp())}_{uuid4().hex[:8]}"
        self.type = event_type
        self.source = source
        self.data = data
        self.timestamp = timestamp or datetime.utcnow().timestamp()
        self.metadata = {
            'causationId': causation_id,
            'correlationId': correlation_id or str(uuid4())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'timestamp': self.timestamp,
            'source': self.source,
            'data': self.data,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            event_id=data['id'],
            event_type=data['type'],
            source=data['source'],
            data=data['data'],
            timestamp=data['timestamp'],
            causation_id=data.get('metadata', {}).get('causationId'),
            correlation_id=data.get('metadata', {}).get('correlationId')
        )
    
    def __str__(self) -> str:
        return f"{self.type} (id: {self.id}, source: {self.source})"
