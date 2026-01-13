import os
import tempfile
import unittest

from services import arc_persistence, arc_weighting


class ArcWeightingTests(unittest.TestCase):
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

    def test_single_arc_single_goal_weights(self):
        # Create an active arc with a goal mapped to 'diplomacy'
        arc = {
            'id': 'arc-100',
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

        candidates = ['diplomacy', 'trade']
        weighted = arc_weighting.weight_actions('actor_1', candidates, self.db_path)

        # find diplomacy
        dip = next((w for w in weighted if w['action'] == 'diplomacy'), None)
        trd = next((w for w in weighted if w['action'] == 'trade'), None)
        self.assertIsNotNone(dip)
        self.assertIsNotNone(trd)

        # base = 1.0; delta = priority * (delta/target) = 2 * 0.5 = 1.0 => final = 2.0
        self.assertAlmostEqual(dip['final_weight'], 2.0)
        self.assertAlmostEqual(trd['final_weight'], 1.0)


if __name__ == '__main__':
    unittest.main()
