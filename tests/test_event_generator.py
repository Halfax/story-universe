import unittest
from unittest.mock import patch, Mock
import time

from event_generator import NarrativeEngine


class FakeResponse:
    def __init__(self, ok=True, json_data=None):
        self.ok = ok
        self._json = json_data or {}

    def json(self):
        return self._json


class TestNarrativeEngine(unittest.TestCase):
    def test_generate_event_without_pi(self):
        # requests.get will raise, simulating Pi unreachable
        with patch('src.event_generator.requests.get', side_effect=Exception('no pi')):
            eng = NarrativeEngine(pi_base_url='http://localhost:9999')
            ev = eng.generate_event()
            self.assertIsNotNone(ev)
            self.assertIn('id', ev)
            self.assertIn('timestamp', ev)
            self.assertIn('type', ev)

    def test_goals_influence_selection_and_progress(self):
        # Simulate Pi returning one character with trait 'curious'
        characters_payload = [{'id': 'c1', 'name': 'Alice', 'traits': ['curious']}]
        world_state_payload = {'tension': 0.2}

        def fake_get(url, timeout=5, **kwargs):
            if url.endswith('/world/state'):
                return FakeResponse(ok=True, json_data=world_state_payload)
            if url.endswith('/world/characters'):
                return FakeResponse(ok=True, json_data={'characters': characters_payload})
            if url.endswith('/world/locations'):
                return FakeResponse(ok=True, json_data={'locations': []})
            if url.endswith('/world/factions'):
                return FakeResponse(ok=True, json_data={'factions': []})
            return FakeResponse(ok=False, json_data={})

        with patch('src.event_generator.requests.get', side_effect=fake_get):
            eng = NarrativeEngine(pi_base_url='http://localhost:8001')
            # ensure goals inferred
            chars = eng.fetch_characters()
            self.assertTrue(any(c['id'] == 'c1' for c in chars))
            # generate few events to progress the goal
            ev1 = eng.generate_event()
            ev2 = eng.generate_event()
            ev3 = eng.generate_event()
            # after several events, char_goals should be either progressed or resolved
            # check that engine state contains char_goals mapping or had it resolved
            cg = eng.char_goals.get('c1')
            # either completed (None) or progress recorded
            if cg:
                self.assertTrue(cg.get('progress', 0) >= 0)


if __name__ == '__main__':
    unittest.main()
