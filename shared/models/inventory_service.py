from typing import Dict, Any, Optional
from .item import Item, InventoryItem, can_equip_item, apply_consumable_effects


class InventoryError(Exception):
    pass


def add_item_to_inventory(owner_type: str, owner_id: str, item: Item, quantity: int = 1) -> InventoryItem:
    inv = InventoryItem(
        id=None,
        owner_type=owner_type,
        owner_id=str(owner_id),
        item_id=int(item.id) if item.id is not None else 0,
        quantity=quantity,
        durability=item.durability_max,
        charges_remaining=item.charges_max,
        equipped=False,
        equip_slot=item.equip_slot,
        metadata={"_item_def": item, "effects": item.effects or {}},
    )
    return inv


def use_inventory_item(inv_item: InventoryItem, target_state: Dict[str, Any]) -> Dict[str, Any]:
    if inv_item is None:
        raise InventoryError("Inventory item is required")
    # Prefer metadata.effects, fall back to metadata._item_def.effects
    effects = inv_item.metadata.get("effects") or (inv_item.metadata.get("_item_def") and getattr(inv_item.metadata.get("_item_def"), "effects", {})) or {}
    new_state = target_state.copy()
    if effects:
        new_state = apply_consumable_effects(effects, target_state)
    # decrement charges or quantity
    if inv_item.charges_remaining is not None:
        inv_item.charges_remaining = max(0, inv_item.charges_remaining - 1)
    else:
        inv_item.quantity = max(0, inv_item.quantity - 1)
    return new_state


def equip_inventory_item(inv_item: InventoryItem, slot: str) -> None:
    if not inv_item:
        raise InventoryError("Inventory item is required")
    item_def = inv_item.metadata.get("_item_def")
    if item_def and not can_equip_item(item_def, slot):
        raise InventoryError("Item cannot be equipped in this slot")
    inv_item.equipped = True
    inv_item.equip_slot = slot


def unequip_inventory_item(inv_item: InventoryItem) -> None:
    if not inv_item:
        raise InventoryError("Inventory item is required")
    inv_item.equipped = False
    inv_item.equip_slot = None
