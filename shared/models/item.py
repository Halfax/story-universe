from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field
import json


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


@dataclass
class Item:
    id: Optional[int]
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
    effects: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        if self.equip_slot:
            d["equip_slot"] = self.equip_slot.value
        d["category"] = self.category.value if isinstance(self.category, ItemCategory) else self.category
        d["effects"] = json.dumps(self.effects)
        d["tags"] = json.dumps(self.tags)
        return d


@dataclass
class InventoryItem:
    id: Optional[int]
    owner_type: str
    owner_id: str
    item_id: int
    quantity: int = 1
    durability: Optional[int] = None
    charges_remaining: Optional[int] = None
    equipped: bool = False
    equip_slot: Optional[EquipSlot] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        if self.equip_slot:
            d["equip_slot"] = self.equip_slot.value
        d["metadata"] = json.dumps(self.metadata)
        return d


# Basic item behaviors

def can_equip_item(item: Item, slot: EquipSlot) -> bool:
    if not item.equippable:
        return False
    if item.equip_slot and item.equip_slot != slot:
        return False
    return True


def apply_consumable_effects(effects: Dict[str, Any], target_state: Dict[str, Any]) -> Dict[str, Any]:
    """Apply simple effects to target_state (e.g., character). Effects is a dict like {"hp": 10}
    This is deliberately small — the Narrative Engine / Chronicle Keeper should implement concrete effect application.
    """
    new_state = target_state.copy()
    for k, v in effects.items():
        if isinstance(v, (int, float)):
            new_state[k] = new_state.get(k, 0) + v
        else:
            # other effect types can be encoded in metadata
            new_state[k] = v
    return new_state
