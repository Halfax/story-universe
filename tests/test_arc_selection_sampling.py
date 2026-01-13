import os
import tempfile
import unittest

import importlib.util
import os
from services import arc_persistence

# Load NarrativeEngine from narrative-engine/src/event_generator.py (handles hyphenated folder)
spec_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'narrative-engine', 'src', 'event_generator.py'))
spec = importlib.util.spec_from_file_location('narrative_event_generator', spec_path)
event_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(event_mod)
NarrativeEngine = event_mod.NarrativeEngine


class ArcSelectionSamplingTests(unittest.TestCase):
    def setUp(self):
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.close()
        self.db_path = tf.name
        arc_persistence.init_db(self.db_path)

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_weighted_sampling_deterministic(self):
        # Create arc giving diplomacy higher weight
        arc = {
            'id': 'arc-sel-1',
            'name': 'Influence Push',
            'state': 'active',
            'participants': ['actor_1'],
            'events': [],
            'goals': [
                {'type': 'expand_influence', 'target_value': 100, 'current_value': 50, 'priority': 2}
            ],
            'data': {}
        }
        arc_persistence.create_arc(self.db_path, arc)

        engine = NarrativeEngine(db_path=self.db_path, seed=42)
        # deterministic: with seed=42 and secure_resource goal both 'explore' and 'trade'
        # have increased weight; with this seed sampling should pick 'trade'
        action = engine._choose_action_for('actor_1')
        self.assertEqual(action, 'trade')


if __name__ == '__main__':
    unittest.main()
