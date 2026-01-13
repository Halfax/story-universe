from pathlib import Path
import sys

repo = Path('.').resolve()
components = [
    (Path('story-universe/chronicle-keeper/src'), Path('src'), ['chronicle_keeper','src']),
    (Path('story-universe/narrative-engine/src'), Path('src'), ['narrative_engine','src']),
]
conflicts = []
for src_root, dest_root, prefixes in components:
    src_root = repo.joinpath(src_root)
    dest_root = repo.joinpath(dest_root)
    if not src_root.exists():
        print(f'source missing: {src_root}')
        continue
    for p in src_root.rglob('*.py'):
        rel = p.relative_to(src_root)
        dest = dest_root.joinpath(rel)
        if dest.exists():
            conflicts.append((p, dest))

if not conflicts:
    print('No destination conflicts detected.')
    sys.exit(0)

print('Detected potential conflicts (destination exists):')
for s,d in conflicts:
    print(f' - {s} -> {d}')
print(f'Total conflicts: {len(conflicts)}')
sys.exit(0)
