"""Model package for shared domain objects.

Expose commonly used types for convenient imports, e.g.:
`from shared.models.item import Item`.
"""

from .item import Item, InventoryItem, ItemCategory, EquipSlot

__all__ = ["Item", "InventoryItem", "ItemCategory", "EquipSlot"]
"""Shared models package."""

from .item import Item, InventoryItem, ItemCategory, EquipSlot

__all__ = ["Item", "InventoryItem", "ItemCategory", "EquipSlot"]
