"""Import items from CSV into the Chronicle Keeper `items` table.

Usage:
    python import_items.py --csv ../data/items.csv --commit

By default the script runs in dry-run mode and reports how many new items
would be inserted. Use `--commit` to write to the DB.
"""
import csv
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CSV_DEFAULT = ROOT / 'data' / 'items.csv'

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', type=str, default=str(CSV_DEFAULT))
    p.add_argument('--commit', action='store_true')
    return p.parse_args()


def normalize_row(r):
    # Map CSV row dict to DB column order
    # Columns in schema: sku,name,description,category,sub_type,weight,stackable,max_stack,
    # equippable,equip_slot,damage_min,damage_max,armor_rating,durability_max,consumable,charges_max,effects,tags
    def to_none(v):
        if v is None or v == '':
            return None
        return v

    def to_float(v):
        try:
            return float(v)
        except Exception:
            return None

    def to_int(v):
        try:
            return int(float(v))
        except Exception:
            return None

    sku = (r.get('sku') or '').strip()
    name = (r.get('name') or '').strip()
    description = (r.get('description') or '').strip()
    category = (r.get('category') or '').strip()
    sub_type = (r.get('sub_type') or '').strip()
    weight = to_float(r.get('weight',''))
    stackable = to_int(r.get('stackable',''))
    max_stack = to_int(r.get('max_stack',''))
    equippable = to_int(r.get('equippable',''))
    equip_slot = to_none(r.get('equip_slot',''))
    damage_min = to_int(r.get('damage_min',''))
    damage_max = to_int(r.get('damage_max',''))
    armor_rating = to_int(r.get('armor_rating',''))
    durability_max = to_int(r.get('durability_max',''))
    consumable = to_int(r.get('consumable',''))
    charges_max = to_int(r.get('charges_max',''))
    effects = to_none(r.get('effects',''))
    tags = to_none(r.get('tags',''))

    return (sku, name, description, category, sub_type, weight, stackable, max_stack,
            equippable, equip_slot, damage_min, damage_max, armor_rating, durability_max,
            consumable, charges_max, effects, tags)


def main():
    args = get_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print('CSV not found:', csv_path)
        sys.exit(1)

    rows = []
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    print(f'Read {len(rows)} rows from {csv_path}')

    try:
        proj_root = Path(__file__).resolve().parents[1]
        if str(proj_root) not in sys.path:
            sys.path.insert(0, str(proj_root))
        from src.db.database import get_connection
    except Exception as e:
        print('Failed to import DB helper:', e)
        sys.exit(1)

    conn = get_connection()
    c = conn.cursor()
    # ensure items table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
    if not c.fetchone():
        print('Items table not found in DB. Run init_db or ensure schema is applied.')
        conn.close()
        sys.exit(1)

    # find existing skus
    c.execute('SELECT sku FROM items')
    existing = set(r[0] for r in c.fetchall())
    to_insert = []
    for r in rows:
        sku = (r.get('sku') or '').strip()
        if not sku:
            continue
        if sku in existing:
            continue
        to_insert.append(normalize_row(r))

    print(f'{len(to_insert)} new items to insert (existing: {len(existing)})')

    if not args.commit:
        print('Dry-run mode; no changes made. Rerun with --commit to insert.')
        conn.close()
        return

    # insert in batches
    sql = ('INSERT INTO items (sku,name,description,category,sub_type,weight,stackable,max_stack,'
           'equippable,equip_slot,damage_min,damage_max,armor_rating,durability_max,consumable,charges_max,effects,tags) '
           'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
    batch = []
    for row in to_insert:
        batch.append(row)
        if len(batch) >= 500:
            c.executemany(sql, batch)
            conn.commit()
            batch = []
    if batch:
        c.executemany(sql, batch)
        conn.commit()

    print(f'Inserted {len(to_insert)} items into DB')
    conn.close()


if __name__ == '__main__':
    main()
