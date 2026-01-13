import os, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(root, 'story-universe'))
print('CWD:', os.getcwd())
print('sys.path[0]:', sys.path[0])
print('sys.path sample:')
for p in sys.path[:5]:
    print(' -', p)
try:
    import shared
    print('shared package found at:', shared.__file__)
    import importlib
    m = importlib.import_module('shared.config')
    print('shared.config found at', m.__file__)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('IMPORT ERROR:', e)
