from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ItemCategory(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    WEARABLE = "wearable"
    MISC = "misc"


class EquipSlot(str, Enum):
    HEAD = "head"
    TORSO = "torso"
    LEGS = "legs"
    HANDS = "hands"
    FEET = "feet"
    NECK = "neck"
    RING = "ring"
    BACK = "back"


class ItemSchema(BaseModel):
    id: Optional[int] = None
    sku: str
    name: str
    description: Optional[str] = ""
    category: ItemCategory = ItemCategory.MISC
    sub_type: Optional[str] = None
    weight: float = 0.0
    stackable: bool = False
    max_stack: int = 1
    equippable: bool = False
    equip_slot: Optional[EquipSlot] = None
    damage_min: Optional[int] = None
    damage_max: Optional[int] = None
    armor_rating: Optional[int] = None
    durability_max: Optional[int] = None
    consumable: bool = False
    charges_max: Optional[int] = None
    effects: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class InventoryItemSchema(BaseModel):
    id: Optional[int] = None
    owner_type: str
    owner_id: str
    item_id: int
    quantity: int = 1
    durability: Optional[int] = None
    charges_remaining: Optional[int] = None
    equipped: bool = False
    equip_slot: Optional[EquipSlot] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CharacterSchema(BaseModel):
    id: Optional[str] = None
    name: str
    faction_id: Optional[str] = None
    traits: Dict[str, Any] = Field(default_factory=dict)
    attributes: Dict[str, Any] = Field(default_factory=lambda: {"hp": 100, "stamina": 100})
    inventory_ids: List[int] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class FactionSchema(BaseModel):
    id: Optional[str] = None
    name: str
    attributes: Dict[str, Any] = Field(default_factory=lambda: {"trust_index": 50})
    relationships: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
