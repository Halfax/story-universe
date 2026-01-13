import sys
import os
from pathlib import Path

# Prevent background clock from starting during tests which can hang the test runner.
os.environ.setdefault("CHRONICLE_DISABLE_CLOCK", "1")

# Ensure local `src` packages are importable for tests.
# This file is placed in chronicle-keeper/tests; we add:
# - chronicle-keeper/src
# - narrative-engine/src (sibling folder)

HERE = Path(__file__).resolve()
# chronicle-keeper folder
CHRON_ROOT = HERE.parent.parent
# Search upward for a `narrative-engine` sibling that contains a `src` directory.
possible_roots = [CHRON_ROOT]
for ancestor in CHRON_ROOT.parents:
    if ancestor == ancestor.parent:
        break
    possible_roots.append(ancestor)

for base in possible_roots:
    candidate = base / 'narrative-engine'
    if candidate.exists() and (candidate / 'src').exists():
        p = str(candidate)
        if p not in sys.path:
            sys.path.insert(0, p)

# also add the chronicle-keeper root so its `src` package is importable
if str(CHRON_ROOT) not in sys.path:
    sys.path.insert(0, str(CHRON_ROOT))
