"""Shared data models for Story Universe components."""

__version__ = "0.1.0"

from .base import Model, Event, Serializable
from .characters import Character, CharacterTrait, Relationship
from .locations import Location, Path, Region
from .items import Item, Inventory, ItemTrait
from .events import (
    WorldEvent,
    NarrativeEvent,
    SystemEvent,
    EventType,
    EventFactory
)

__all__ = [
    'Model',
    'Event',
    'Serializable',
    'Character',
    'CharacterTrait',
    'Relationship',
    'Location',
    'Path',
    'Region',
    'Item',
    'Inventory',
    'ItemTrait',
    'WorldEvent',
    'NarrativeEvent',
    'SystemEvent',
    'EventType',
    'EventFactory'
]
