"""Faction name generator and writer.

Usage:
    python tools/faction_generator.py --count 500 --out data/faction_names.csv

Generates a diverse set of faction names across categories:
  - fantasy_factions
  - fantasy_races
  - real_inspired
  - sci_fi

This script also includes simple templates and combines prefixes/suffixes
to create varied names. It can be extended with more wordlists.
"""
import csv
import random
import argparse
from pathlib import Path

CATEGORY_TEMPLATES = {
    'fantasy_factions': [
        'Order of {X}', 'The {X} Circle', '{X} Guild', 'House {X}',
        'Clan {X}', 'The {X} Covenant', 'Brotherhood of {X}',
        'Sisters of {X}', 'The {X} Enclave', '{X} Legion', 'The {X} Keep'
    ],
    'fantasy_races': [
        '{X}folk', '{X}kin', 'The {X}born', 'People of {X}',
        '{X} Clans', 'The {X} Tribes', '{X} Host', '{X} Nomads'
    ],
    'real_inspired': [
        '{X} Confederation', '{X} Coalition', '{X} Republic',
        '{X} Alliance', '{X} League', '{X} Union', '{X} Directorate',
        '{X} Syndicate', '{X} Consortium'
    ],
    'sci_fi': [
        'Interstellar {X}', 'The {X} Directorate', '{X} Collective',
        '{X} Armada', '{X} Conglomerate', 'The {X} Nexus',
        '{X} Syndicate', '{X} Consortium', 'The {X} Accord'
    ]
}

PREFIXES = [
    'Crimson', 'Azure', 'Silver', 'Obsidian', 'Golden', 'Emerald', 'Iron',
    'Storm', 'Shadow', 'Sun', 'Moon', 'Star', 'Thunder', 'Winter', 'Autumn',
    'Dawn', 'Dusk', 'Radiant', 'Silent', 'Feral', 'Verdant', 'Sacred'
]

NOUNS = [
    'Vanguard', 'Warden', 'Spear', 'Hammer', 'Lotus', 'Raven', 'Wolf', 'Serpent',
    'Phoenix', 'Dragon', 'Briar', 'Beacon', 'Coven', 'Thorn', 'Grove', 'Keep',
    'Banner', 'Harbor', 'Citadel', 'Forge', 'Watch', 'Crest', 'Hollow', 'Eclipse'
]

ROOTS = [
    'Alder', 'Bright', 'Elden', 'Fall', 'Galen', 'Harrow', 'Ithil', 'Korr',
    'Lorien', 'Mire', 'Ner', 'Orin', 'Pelor', 'Quill', 'Rhon', 'Sable',
    'Tarn', 'Umbra', 'Voss', 'Wyr', 'Xan', 'Yar', 'Zeph'
]

REAL_BASES = [
    'Northreach', 'Southport', 'Westfold', 'Eastmarch', 'Highmere', 'Lowgate',
    'Silverfield', 'Ironhold', 'Redshore', 'Goldcrest', 'Stonehelm', 'Rivermark'
]

SCI_BASES = [
    'Nova', 'Quantum', 'Aegis', 'Helix', 'Orbital', 'Celest', 'Novae', 'Zenith',
    'Strata', 'Pulse', 'Epoch', 'Beacon'
]


def make_name(category: str) -> str:
    if category == 'fantasy_factions':
        template = random.choice(CATEGORY_TEMPLATES[category])
        x = random.choice(PREFIXES + NOUNS + ROOTS + REAL_BASES)
        return template.replace('{X}', x)
    if category == 'fantasy_races':
        template = random.choice(CATEGORY_TEMPLATES[category])
        x = random.choice(ROOTS + PREFIXES)
        return template.replace('{X}', x)
    if category == 'real_inspired':
        template = random.choice(CATEGORY_TEMPLATES[category])
        x = random.choice(REAL_BASES + ROOTS + NOUNS)
        return template.replace('{X}', x)
    if category == 'sci_fi':
        template = random.choice(CATEGORY_TEMPLATES[category])
        x = random.choice(SCI_BASES + PREFIXES + NOUNS)
        return template.replace('{X}', x)
    return 'Unknown'


def generate(count: int = 500):
    per_cat = max(1, count // 4)
    rows = []
    cats = ['fantasy_factions', 'fantasy_races', 'real_inspired', 'sci_fi']
    for cat in cats:
        seen = set()
        attempts = 0
        while len([r for r in rows if r[0] == cat]) < per_cat and attempts < per_cat * 10:
            attempts += 1
            name = make_name(cat)
            if name in seen:
                continue
            seen.add(name)
            rows.append((cat, name))
    # If short due to integer division, top up with mixed names
    while len(rows) < count:
        cat = random.choice(cats)
        name = make_name(cat)
        if name not in [r[1] for r in rows]:
            rows.append((cat, name))
    random.shuffle(rows)
    return rows


def write_csv(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['category', 'name'])
        for r in rows:
            w.writerow(r)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=500)
    parser.add_argument('--out', type=str, default='chronicle-keeper/data/faction_names.csv')
    args = parser.parse_args()
    rows = generate(args.count)
    write_csv(rows, Path(args.out))
    print(f'Wrote {len(rows)} names to {args.out}')


if __name__ == '__main__':
    main()
