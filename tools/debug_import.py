import sys
import importlib

# Inject project roots so tests can import `src.*` modules regardless of environment
SYS_ROOT = r"C:\Users\arhal_iz5093n\Desktop\projects\story-universe\story-universe\narrative-engine"
CK_ROOT = r"C:\Users\arhal_iz5093n\Desktop\projects\story-universe\story-universe\chronicle-keeper"
for p in (SYS_ROOT, CK_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

print('--- sys.path (head) ---')
for p in sys.path[:6]:
    print(p)

print('\n--- attempting import src.event_generator ---')
try:
    importlib.import_module('src.event_generator')
    print('IMPORT_OK')
except Exception:
    import traceback
    traceback.print_exc()

print('\n--- done ---')
