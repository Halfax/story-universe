import os
import sys
import unittest

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
inner_story = os.path.join(root, 'story-universe')
chronicle = os.path.join(inner_story, 'chronicle-keeper')
narr = os.path.join(inner_story, 'narrative-engine')

# Ensure imports like `shared.config` and `src.*` resolve
sys.path.insert(0, chronicle)
sys.path.insert(0, narr)
sys.path.insert(0, inner_story)
sys.path.insert(0, root)

print('sys.path (start):')
for p in sys.path[:4]:
    print(' -', p)

loader = unittest.TestLoader()

print('\nRunning chronicle-keeper tests...')
suite1 = loader.discover(start_dir=os.path.join(chronicle, 'tests'))
res1 = unittest.TextTestRunner(verbosity=2).run(suite1)

print('\nRunning narrative-engine tests...')
suite2 = loader.discover(start_dir=os.path.join(narr, 'tests'))
res2 = unittest.TextTestRunner(verbosity=2).run(suite2)

ok = res1.wasSuccessful() and res2.wasSuccessful()
if not ok:
    sys.exit(1)
