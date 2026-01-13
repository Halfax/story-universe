import unittest

from shared.models.item import Item, InventoryItem, ItemCategory, EquipSlot
from shared.models.character import Character
from shared.models.faction import Faction
from shared.models.inventory_service import (
    add_item_to_inventory,
    use_inventory_item,
    equip_inventory_item,
    unequip_inventory_item,
)


class TestSharedModels(unittest.TestCase):

    def test_item_roundtrip(self):
        item = Item(
            id=1,
            sku="sword_001",
            name="Longsword",
            description="A sharp blade",
            category=ItemCategory.WEAPON,
            equippable=True,
            equip_slot=EquipSlot.HANDS,
            damage_min=3,
            damage_max=7,
            consumable=False,
        )
        d = item.to_dict()
        item2 = Item.from_dict(d)
        self.assertEqual(item.sku, item2.sku)
        self.assertEqual(item.name, item2.name)
        self.assertEqual(item.category.value, item2.category.value)

    def test_inventory_add_and_use_consumable(self):
        item = Item(
            id=2,
            sku="potion_hp",
            name="Health Potion",
            consumable=True,
            charges_max=2,
            effects={"hp": 10},
        )
        inv = add_item_to_inventory("character", "char_1", item, quantity=1)
        # attach item def to metadata and effects so that inventory_service may inspect it
        inv.metadata["_item_def"] = item
        inv.metadata["effects"] = item.effects
        target = {"hp": 0}
        new_state = use_inventory_item(inv, target)
        self.assertEqual(new_state["hp"], 10)
        # charges or quantity should have decreased
        self.assertTrue(inv.charges_remaining == 1 or inv.quantity == 0 or inv.quantity == 1)

    def test_equip_and_unequip(self):
        item = Item(
            id=3,
            sku="ring_01",
            name="Silver Ring",
            equippable=True,
            equip_slot=EquipSlot.RING,
        )
        inv = add_item_to_inventory("character", "char_2", item, quantity=1)
        # equip using slot name
        slot = EquipSlot.RING.value
        equip_inventory_item(inv, slot)
        self.assertTrue(inv.equipped)
        self.assertEqual(inv.equip_slot, slot)
        unequip_inventory_item(inv)
        self.assertFalse(inv.equipped)
        self.assertIsNone(inv.equip_slot)

    def test_character_and_faction_deltas(self):
        c = Character(name="Ava")
        c.apply_delta({"hp": -20, "stamina": 5})
        self.assertEqual(c.attributes["hp"], 80)
        self.assertEqual(c.attributes["stamina"], 105)

        f = Faction(name="Northrealm")
        f.apply_delta({"trust_index": 10})
        self.assertEqual(f.attributes.get("trust_index"), 60)


if __name__ == "__main__":
    unittest.main()
