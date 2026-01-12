from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from .base import Entity

class ItemRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    TREASURE = "treasure"
    QUEST = "quest"
    TOOL = "tool"
    CONTAINER = "container"
    OTHER = "other"

class ItemEffect(BaseModel):
    """Effect that an item can have when used."""
    type: str = Field(..., description="Effect type (e.g., 'heal', 'damage', 'buff')")
    value: Union[int, float, str, Dict] = Field(..., description="Effect value or parameters")
    duration: Optional[float] = Field(None, description="Effect duration in seconds")
    description: str = Field("", description="Human-readable effect description")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "heal",
                "value": 10,
                "duration": 0,
                "description": "Restores 10 health points"
            }
        }

class Item(Entity):
    """An item that can be owned, traded, or used."""
    type: str = Field("item", const=True)
    item_type: ItemType = Field(ItemType.OTHER)
    rarity: ItemRarity = Field(ItemRarity.COMMON)
    weight: float = Field(0.0, ge=0, description="Weight in kilograms")
    value: int = Field(0, ge=0, description="Base value in copper pieces")
    max_stack: int = Field(1, ge=1, description="Maximum stack size")
    is_equippable: bool = Field(False, description="Can be equipped")
    is_consumable: bool = Field(False, description="Consumed on use")
    is_quest_item: bool = Field(False, description="Required for quests")
    effects: List[ItemEffect] = Field(
        default_factory=list,
        description="Effects when used"
    )
    requirements: Dict[str, Union[int, str, List[str]]] = Field(
        default_factory=dict,
        description="Requirements to use/equip"
    )
    
    class Config(Entity.Config):
        schema_extra = {
            **Entity.Config.schema_extra["example"],
            "type": "item",
            "item_type": "consumable",
            "rarity": "uncommon",
            "weight": 0.1,
            "value": 50,
            "max_stack": 10,
            "is_consumable": True,
            "effects": [
                {
                    "type": "heal",
                    "value": 10,
                    "description": "Restores 10 health points"
                }
            ]
        }

class InventorySlot(BaseModel):
    """A slot in an inventory containing an item and quantity."""
    item_id: str = Field(..., description="Reference to item")
    quantity: int = Field(1, ge=1, description="Number of items in this slot")
    equipped: bool = Field(False, description="Is this item equipped?")
    condition: float = Field(1.0, ge=0.0, le=1.0, description="Condition (1.0 = new)")
    
    @validator('quantity')
    def validate_quantity(cls, v, values, **kwargs):
        if 'item' in values and v > values['item'].max_stack:
            raise ValueError(f"Cannot stack more than {values['item'].max_stack} of this item")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "item_id": "item-123",
                "quantity": 5,
                "equipped": False,
                "condition": 0.9
            }
        }

class Inventory(BaseModel):
    """A collection of items owned by a character or container."""
    owner_id: str = Field(..., description="ID of the owner")
    max_weight: Optional[float] = Field(None, description="Maximum carry weight in kg")
    max_slots: Optional[int] = Field(None, description="Maximum number of slots")
    slots: Dict[str, InventorySlot] = Field(
        default_factory=dict,
        description="Item slots in this inventory"
    )
    
    @property
    def total_weight(self) -> float:
        """Calculate total weight of all items in the inventory."""
        # Note: This would need access to the item database to get weights
        return sum(slot.quantity * slot.item.weight for slot in self.slots.values())
    
    @property
    def used_slots(self) -> int:
        """Number of slots currently in use."""
        return len(self.slots)
    
    def can_add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if an item can be added to the inventory."""
        # Implementation would check weight and slot limits
        # and handle stacking logic
        return True
    
    class Config:
        schema_extra = {
            "example": {
                "owner_id": "char-123",
                "max_weight": 50.0,
                "max_slots": 30,
                "slots": {
                    "slot1": InventorySlot.Config.schema_extra["example"]
                }
            }
        }
