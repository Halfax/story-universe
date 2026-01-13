"""Model package for shared domain objects.

Expose commonly used types for convenient imports, e.g.:
`from shared.models.item import Item`.
"""

from .base import Model, Event, Serializable
from .item import Item, InventoryItem, ItemCategory, EquipSlot
from .character import Character
from .faction import Faction
from .inventory_service import (
	add_item_to_inventory,
	use_inventory_item,
	equip_inventory_item,
	unequip_inventory_item,
	InventoryError,
)

__all__ = [
	"Model",
	"Event",
	"Serializable",
	"Item",
	"InventoryItem",
	"ItemCategory",
	"EquipSlot",
	"Character",
	"Faction",
	"add_item_to_inventory",
	"use_inventory_item",
	"equip_inventory_item",
	"unequip_inventory_item",
	"InventoryError",
]
