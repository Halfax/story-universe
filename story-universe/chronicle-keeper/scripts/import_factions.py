"""Import faction names from CSV into the Chronicle Keeper `factions` table.

Usage:
    python import_factions.py --csv ../data/faction_names.csv --commit

By default the script runs in dry-run mode and reports how many new factions
would be inserted. Use `--commit` to write to the DB.
"""
import csv
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CSV_DEFAULT = ROOT / 'data' / 'faction_names.csv'

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', type=str, default=str(CSV_DEFAULT))
    p.add_argument('--commit', action='store_true')
    return p.parse_args()


def main():
    args = get_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print('CSV not found:', csv_path)
        sys.exit(1)

    # read names
    names = []
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            name = (r.get('name') or '').strip()
            if name:
                names.append(name)

    unique_names = list(dict.fromkeys(names))
    print(f'Read {len(names)} rows, {len(unique_names)} unique names')

    # import using the Pi DB connection
    try:
        # ensure project root is on sys.path so `src` package resolves
        proj_root = Path(__file__).resolve().parents[1]
        if str(proj_root) not in sys.path:
            sys.path.insert(0, str(proj_root))
        from src.db.database import get_connection
    except Exception as e:
        print('Failed to import DB helper:', e)
        sys.exit(1)

    conn = get_connection()
    c = conn.cursor()
    # ensure factions table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='factions'")
    if not c.fetchone():
        print('Factions table not found in DB. Run init_db or ensure schema is applied.')
        conn.close()
        sys.exit(1)

    # find existing names
    c.execute('SELECT name FROM factions')
    existing = set(r[0] for r in c.fetchall())
    to_insert = [n for n in unique_names if n not in existing]
    print(f'{len(to_insert)} new factions to insert (existing: {len(existing)})')

    if not args.commit:
        print('Dry-run mode; no changes made. Rerun with --commit to insert.')
        conn.close()
        return

    # insert in batches
    batch = []
    for name in to_insert:
        batch.append((name, None, '{}'))
        if len(batch) >= 500:
            c.executemany('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', batch)
            conn.commit()
            batch = []
    if batch:
        c.executemany('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', batch)
        conn.commit()

    print(f'Inserted {len(to_insert)} factions into DB')
    conn.close()


if __name__ == '__main__':
    main()
