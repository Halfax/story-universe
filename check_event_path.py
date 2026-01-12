from pathlib import Path
here = Path('story-universe/chronicle-keeper/tests/test_narrative_engine.py').resolve()
print('here:', here)
for ancestor in here.parents:
    candidate = ancestor / 'narrative-engine' / 'src' / 'event_generator.py'
    print('checking', candidate, 'exists=', candidate.exists())
