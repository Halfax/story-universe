import os
import sys
import unittest
from pathlib import Path

# Run tests from repository root and prefer a flattened `src/` layout when present.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(repo_root)

src_dir = os.path.join(repo_root, 'src')
if os.path.isdir(src_dir):
	sys.path.insert(0, src_dir)
sys.path.insert(0, repo_root)

print('Running tests from', os.getcwd())
print('sys.path[0] =', sys.path[0])
print('Top sys.path entries:')
for p in sys.path[:5]:
	print(' -', p)

# Find a tests directory to run; prefer flattened locations but fall back to existing layout.
candidate_paths = [
	os.path.join(repo_root, 'tests'),
	os.path.join(repo_root, 'src', 'chronicle_keeper', 'tests'),
	os.path.join(repo_root, 'story-universe', 'chronicle-keeper', 'tests'),
	os.path.join(repo_root, 'story-universe', 'narrative-engine', 'tests'),
]
tests_to_run = None
for p in candidate_paths:
	if os.path.isdir(p):
		tests_to_run = p
		break

if not tests_to_run:
	print('No tests directory found. Checked:', candidate_paths)
	sys.exit(2)

loader = unittest.TestLoader()
suite = loader.discover(start_dir=tests_to_run)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

sys.exit(0 if result.wasSuccessful() else 1)
