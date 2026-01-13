import sqlite3
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.inventory import pickup_item, list_inventory, use_inventory_item, equip_inventory_item
from services.event_consumer import _apply_item_use_effects, handle_event


def _make_conn_with_schema():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'db', 'schema.sql'))
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    cur.executescript(sql)
    # Ensure auxiliary tables used by consumers/tests exist
    cur.execute('''CREATE TABLE IF NOT EXISTS system_state (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        type TEXT,
        description TEXT,
        involved_characters TEXT,
        involved_locations TEXT,
        metadata TEXT
    )''')
    conn.commit()
    return conn


def test_pickup_stackable_and_equip_flow():
    conn = _make_conn_with_schema()
    cur = conn.cursor()
    # create a stackable consumable item
    cur.execute("INSERT INTO items (sku, name, stackable, max_stack, consumable, effects) VALUES (?, ?, ?, ?, ?, ?)", ('potion-01', 'Health Potion', 1, 10, 1, json.dumps({'hp': 10})))
    potion_id = cur.lastrowid

    # pickup 3
    res = pickup_item('character', '1', potion_id, 3, db_conn_getter=lambda: conn)
    assert res['quantity'] == 3

    # pickup 2 more -> total 5
    res2 = pickup_item('character', '1', potion_id, 2, db_conn_getter=lambda: conn)
    assert res2['quantity'] == 5

    rows = list_inventory('character', '1', db_conn_getter=lambda: conn)
    assert len(rows) == 1
    inv = rows[0]
    assert inv['quantity'] == 5

    # use 2 potions
    use_res = use_inventory_item(inv['id'], 2, db_conn_getter=lambda: conn)
    assert use_res['consumed'] == 2

    rows_after = list_inventory('character', '1', db_conn_getter=lambda: conn)
    assert rows_after[0]['quantity'] == 3

    # create equippable sword
    cur.execute("INSERT INTO items (sku, name, equippable, equip_slot) VALUES (?, ?, ?, ?)", ('sword-01', 'Short Sword', 1, 'hands'))
    sword_id = cur.lastrowid
    # pickup sword
    pick = pickup_item('character', '1', sword_id, 1, db_conn_getter=lambda: conn)
    sword_inv_id = pick['inventory_id']
    # equip sword
    eq = equip_inventory_item(sword_inv_id, 'hands', db_conn_getter=lambda: conn)
    assert eq['equipped'] is True

    # ensure only one item in hands
    cur.execute("SELECT COUNT(*) FROM inventory WHERE owner_type=? AND owner_id=? AND equip_slot=? AND equipped=1", ('character', '1', 'hands'))
    count = cur.fetchone()[0]
    assert count == 1


def test_event_consumer_applies_effects():
    conn = _make_conn_with_schema()
    cur = conn.cursor()
    # create item with effects
    cur.execute("INSERT INTO items (sku, name, consumable, effects) VALUES (?, ?, ?, ?)", ('potion-02', 'Big Potion', 1, json.dumps({'hp': 50})))
    item_id = cur.lastrowid

    # create inventory row for character 1
    cur.execute("INSERT INTO inventory (owner_type, owner_id, item_id, quantity) VALUES (?, ?, ?, ?)", ('character', '1', item_id, 1))
    inv_id = cur.lastrowid

    # ensure character_state has initial state
    cur.execute("INSERT OR REPLACE INTO character_state (character_id, state, last_updated) VALUES (?, ?, ?)", (1, json.dumps({'hp': 0}), 0))
    conn.commit()

    event = {'type': 'item_use', 'inventory_id': inv_id, 'character_id': '1', 'quantity': 1}
    # Call consumer
    new_state = handle_event(event, db_conn_getter=lambda: conn)
    assert new_state['hp'] == 50


