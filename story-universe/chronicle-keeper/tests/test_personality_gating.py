import unittest
import sqlite3
from pathlib import Path


class TestPersonalityGating(unittest.TestCase):
    def setUp(self):
        schema_path = Path(__file__).resolve().parents[1] / 'src' / 'db' / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        self.conn = sqlite3.connect(':memory:')
        self.conn.executescript(schema)
        c = self.conn.cursor()
        # ensure a character exists
        c.execute('INSERT INTO characters (name, age, traits, location_id, status) VALUES (?, ?, ?, ?, ?)', ('Tester', 30, '[]', None, 'alive'))
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_aggressive_allows_attack_at_lower_trust(self):
        c = self.conn.cursor()
        # create faction with low trust
        c.execute('INSERT INTO factions (name, personality_traits) VALUES (?, ?)', ('AggressiveFaction', '{"aggressive": 0.9}'))
        fid = c.lastrowid
        c.execute('INSERT INTO faction_metrics (faction_id, trust, power, resources, influence) VALUES (?, ?, ?, ?, ?)', (fid, 0.03, 1, 10, 0))
        self.conn.commit()

        from src.services.continuity import ContinuityValidator
        validator = ContinuityValidator(db_conn_getter=lambda: self.conn)
        event = {'type': 'faction_event', 'source_faction_id': fid, 'target_faction_id': fid, 'action': 'attack'}
        valid, reason = validator.validate_event(event)
        # aggressive factions have lower attack threshold, so this should be allowed
        self.assertTrue(valid, msg=f"Expected aggressive faction to allow attack, got: {reason}")

    def test_diplomatic_allows_alliance_when_default_blocks(self):
        c = self.conn.cursor()
        # create non-diplomatic faction with moderate trust
        c.execute('INSERT INTO factions (name, personality_traits) VALUES (?, ?)', ('NeutralFaction', '{}'))
        fid_n = c.lastrowid
        c.execute('INSERT INTO faction_metrics (faction_id, trust, power, resources, influence) VALUES (?, ?, ?, ?, ?)', (fid_n, 0.15, 1, 10, 0))

        # create diplomatic faction
        c.execute('INSERT INTO factions (name, personality_traits) VALUES (?, ?)', ('DiplomaticFaction', '{"diplomatic": 0.9}'))
        fid_d = c.lastrowid
        c.execute('INSERT INTO faction_metrics (faction_id, trust, power, resources, influence) VALUES (?, ?, ?, ?, ?)', (fid_d, 0.15, 1, 10, 0))
        self.conn.commit()

        from src.services.continuity import ContinuityValidator
        validator = ContinuityValidator(db_conn_getter=lambda: self.conn)

        # neutral faction should be blocked forming alliance at trust=0.15 (default threshold 0.2)
        event_n = {'type': 'faction_event', 'source_faction_id': fid_n, 'target_faction_id': fid_n, 'action': 'form_alliance'}
        valid_n, reason_n = validator.validate_event(event_n)
        self.assertFalse(valid_n)

        # diplomatic faction with same trust should be allowed (threshold lowered)
        event_d = {'type': 'faction_event', 'source_faction_id': fid_d, 'target_faction_id': fid_d, 'action': 'form_alliance'}
        valid_d, reason_d = validator.validate_event(event_d)
        self.assertTrue(valid_d, msg=f"Expected diplomatic faction to allow alliance, got: {reason_d}")


if __name__ == '__main__':
    unittest.main()
