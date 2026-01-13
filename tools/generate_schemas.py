"""Generate JSON Schema files for shared Pydantic models."""
from pathlib import Path
from shared.models.schemas import (
    ItemSchema,
    InventoryItemSchema,
    CharacterSchema,
    FactionSchema,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "schemas"
OUT_DIR.mkdir(parents=True, exist_ok=True)

mapping = {
    "item.schema.json": ItemSchema,
    "inventory_item.schema.json": InventoryItemSchema,
    "character.schema.json": CharacterSchema,
    "faction.schema.json": FactionSchema,
}

for fname, model in mapping.items():
    schema = model.schema_json(indent=2)
    (OUT_DIR / fname).write_text(schema, encoding="utf-8")
    print(f"Wrote {OUT_DIR / fname}")
