from typing import Optional, Dict, Any, List
from .schemas import ItemSchema, InventoryItemSchema, ItemCategory, EquipSlot


# Backwards-compatible Pydantic wrappers
class Item(ItemSchema):
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        return cls.model_validate(data)


class InventoryItem(InventoryItemSchema):
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InventoryItem":
        return cls.model_validate(data)


def can_equip_item(item: Item, slot: EquipSlot) -> bool:
    if not item.equippable:
        return False
    if item.equip_slot and item.equip_slot != slot:
        return False
    return True


def apply_consumable_effects(effects: Dict[str, Any], target_state: Dict[str, Any]) -> Dict[str, Any]:
    new_state = target_state.copy()
    for k, v in effects.items():
        if isinstance(v, (int, float)):
            new_state[k] = new_state.get(k, 0) + v
        else:
            new_state[k] = v
    return new_state
