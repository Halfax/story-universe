"""Seed or update faction metrics from CSV.

CSV columns: name,trust,power,resources,influence

Usage:
  python seed_faction_metrics.py --csv ../data/faction_metrics.csv [--create] [--commit]

By default runs in dry-run mode and reports planned upserts.
"""
import csv
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CSV_DEFAULT = ROOT / 'data' / 'faction_metrics.csv'

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', type=str, default=str(CSV_DEFAULT))
    p.add_argument('--create', action='store_true', help='Create missing factions')
    p.add_argument('--commit', action='store_true', help='Apply changes to DB')
    return p.parse_args()


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
            name = (r.get('name') or '').strip()
            if not name:
                continue
            try:
                trust = float(r.get('trust')) if r.get('trust') not in (None, '') else None
            except Exception:
                trust = None
            def int_or_none(x):
                try:
                    return int(x) if x not in (None, '') else None
                except Exception:
                    return None
            power = int_or_none(r.get('power'))
            resources = int_or_none(r.get('resources'))
            influence = int_or_none(r.get('influence'))
            rows.append({'name': name, 'trust': trust, 'power': power, 'resources': resources, 'influence': influence})

    # Import DB helper
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

    planned = []
    for r in rows:
        name = r['name']
        c.execute('SELECT id FROM factions WHERE name = ?', (name,))
        row = c.fetchone()
        if not row:
            if not args.create:
                planned.append((name, 'missing-faction'))
                continue
            # create faction row
            c.execute('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', (name, None, '{}'))
            fid = c.lastrowid
            planned.append((name, 'created-faction', fid))
        else:
            fid = row[0]
        # check existing metrics
        c.execute('SELECT faction_id FROM faction_metrics WHERE faction_id = ?', (fid,))
        exists = bool(c.fetchone())
        planned.append((name, 'upsert-metrics', fid, r['trust'], r['power'], r['resources'], r['influence']))
        if args.commit:
            if not exists:
                c.execute('INSERT INTO faction_metrics (faction_id, trust, power, resources, influence) VALUES (?, ?, ?, ?, ?)', (fid, float(r['trust'] or 0.5), int(r['power'] or 0), int(r['resources'] or 0), int(r['influence'] or 0)))
            else:
                updates = []
                params = []
                if r['trust'] is not None:
                    updates.append('trust = ?')
                    params.append(float(r['trust']))
                if r['power'] is not None:
                    updates.append('power = ?')
                    params.append(int(r['power']))
                if r['resources'] is not None:
                    updates.append('resources = ?')
                    params.append(int(r['resources']))
                if r['influence'] is not None:
                    updates.append('influence = ?')
                    params.append(int(r['influence']))
                if updates:
                    params.append(fid)
                    c.execute('UPDATE faction_metrics SET ' + ', '.join(updates) + ' WHERE faction_id = ?', params)

    if args.commit:
        conn.commit()

    conn.close()

    print('Planned actions:')
    for p in planned:
        print(' -', p)


if __name__ == '__main__':
    main()
