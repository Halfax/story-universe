import sqlite3
import json
from typing import Optional, Callable, Dict, Any, List



def _get_conn(db_conn_getter: Optional[Callable[[], Any]] = None) -> Any:
    # Lazy import to avoid initializing DB_PATH at module import time
    if db_conn_getter:
        return db_conn_getter()
    from src.db.database import get_connection
    return get_connection()


def list_inventory(owner_type: str, owner_id: str, db_conn_getter: Optional[Callable[[], sqlite3.Connection]] = None) -> List[Dict[str, Any]]:
    conn = _get_conn(db_conn_getter)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT i.*, it.name as item_name, it.stackable, it.max_stack, it.equippable, it.equip_slot as item_equip_slot, it.consumable FROM inventory i LEFT JOIN items it ON i.item_id = it.id WHERE owner_type=? AND owner_id=?", (owner_type, owner_id))
    rows = [dict(r) for r in c.fetchall()]
    return rows


def pickup_item(owner_type: str, owner_id: str, item_id: int, quantity: int = 1, db_conn_getter: Optional[Callable[[], sqlite3.Connection]] = None) -> Dict[str, Any]:
    conn = _get_conn(db_conn_getter)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Load item
    c.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = c.fetchone()
    if not item:
        raise ValueError("item not found")

    stackable = bool(item["stackable"])
    max_stack = item["max_stack"] or 1

    try:
        # Use transaction
        with conn:
            if stackable:
                # Try to find existing inventory entry for same owner and item
                c.execute("SELECT * FROM inventory WHERE owner_type=? AND owner_id=? AND item_id=? AND equipped=0", (owner_type, owner_id, item_id))
                row = c.fetchone()
                if row:
                    new_qty = row["quantity"] + quantity
                    if new_qty > max_stack:
                        # Fill to max, return remainder
                        remainder = new_qty - max_stack
                        c.execute("UPDATE inventory SET quantity=? WHERE id=?", (max_stack, row["id"]))
                        return {"inventory_id": row["id"], "quantity": max_stack, "remainder": remainder}
                    else:
                        c.execute("UPDATE inventory SET quantity=? WHERE id=?", (new_qty, row["id"]))
                        return {"inventory_id": row["id"], "quantity": new_qty}
            # Otherwise insert new inventory row
            c.execute("INSERT INTO inventory (owner_type, owner_id, item_id, quantity, durability, charges_remaining, equipped, equip_slot, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                owner_type, owner_id, item_id, quantity, None, None, 0, None, json.dumps({})
            ))
            inv_id = c.lastrowid
            return {"inventory_id": inv_id, "quantity": quantity}
    finally:
        try:
            # If db_conn_getter provided a persistent connection (e.g., test using same in-memory conn), don't close.
            if db_conn_getter is None:
                conn.close()
        except Exception:
            pass


def use_inventory_item(inventory_id: int, quantity: int = 1, db_conn_getter: Optional[Callable[[], sqlite3.Connection]] = None) -> Dict[str, Any]:
    conn = _get_conn(db_conn_getter)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT i.*, it.consumable, it.effects FROM inventory i JOIN items it ON i.item_id = it.id WHERE i.id=?", (inventory_id,))
    row = c.fetchone()
    if not row:
        raise ValueError("inventory item not found")

    if not row["consumable"]:
        raise ValueError("item is not consumable")

    effects = json.loads(row["effects"] or "{}") if "effects" in row.keys() else {}

    try:
        with conn:
            new_qty = row["quantity"] - quantity
            if new_qty <= 0:
                c.execute("DELETE FROM inventory WHERE id=?", (inventory_id,))
            else:
                c.execute("UPDATE inventory SET quantity=? WHERE id=?", (new_qty, inventory_id))
        return {"inventory_id": inventory_id, "consumed": quantity, "effects": effects}
    finally:
        if db_conn_getter is None:
            conn.close()


def equip_inventory_item(inventory_id: int, equip_slot: str, db_conn_getter: Optional[Callable[[], sqlite3.Connection]] = None) -> Dict[str, Any]:
    conn = _get_conn(db_conn_getter)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT i.*, it.equippable, it.equip_slot as item_equip_slot FROM inventory i JOIN items it ON i.item_id = it.id WHERE i.id=?", (inventory_id,))
    row = c.fetchone()
    if not row:
        raise ValueError("inventory item not found")
    if not row["equippable"]:
        raise ValueError("item is not equippable")
    item_slot = row["item_equip_slot"]
    if item_slot and item_slot != equip_slot:
        raise ValueError("item cannot be equipped in that slot")

    owner_type = row["owner_type"]
    owner_id = row["owner_id"]

    try:
        with conn:
            # Unequip any other item in the same slot for this owner
            c.execute("UPDATE inventory SET equipped=0, equip_slot=NULL WHERE owner_type=? AND owner_id=? AND equip_slot=?", (owner_type, owner_id, equip_slot))
            # Equip this item
            c.execute("UPDATE inventory SET equipped=1, equip_slot=? WHERE id=?", (equip_slot, inventory_id))
        return {"inventory_id": inventory_id, "equipped": True, "equip_slot": equip_slot}
    finally:
        if db_conn_getter is None:
            conn.close()
