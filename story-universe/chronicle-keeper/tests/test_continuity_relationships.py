import unittest
import sqlite3
from pathlib import Path


class TestContinuityValidatorRelationships(unittest.TestCase):
    def setUp(self):
        schema_path = Path(__file__).resolve().parents[1] / 'src' / 'db' / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        self.conn = sqlite3.connect(':memory:')
        self.conn.executescript(schema)
        c = self.conn.cursor()
        # create two factions and a character
        c.execute('INSERT INTO factions (name) VALUES (?)', ('A',))
        self.fid_a = c.lastrowid
        c.execute('INSERT INTO factions (name) VALUES (?)', ('B',))
        self.fid_b = c.lastrowid
        c.execute('INSERT INTO characters (name, age, traits, location_id, status) VALUES (?, ?, ?, ?, ?)', ('Tester', 30, '[]', None, 'alive'))
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_relationship_cooldown_blocks_attack(self):
        c = self.conn.cursor()
        import time
        now = int(time.time())
        # set relationship with active cooldown
        c.execute('INSERT INTO faction_relationships (source_faction_id, target_faction_id, relationship_type, strength, cooldown_until) VALUES (?, ?, ?, ?, ?)', (self.fid_a, self.fid_b, 'rival', -0.5, now + 3600))
        self.conn.commit()

        from src.services.continuity import ContinuityValidator
        validator = ContinuityValidator(db_conn_getter=lambda: self.conn)
        event = {'type': 'faction_event', 'source_faction_id': self.fid_a, 'target_faction_id': self.fid_b, 'action': 'attack'}
        valid, reason = validator.validate_event(event)
        self.assertFalse(valid)
        self.assertIn('cooldown', reason)

    def test_ally_blocks_attack(self):
        c = self.conn.cursor()
        c.execute('INSERT INTO faction_relationships (source_faction_id, target_faction_id, relationship_type, strength) VALUES (?, ?, ?, ?)', (self.fid_a, self.fid_b, 'ally', 0.9))
        self.conn.commit()
        from src.services.continuity import ContinuityValidator
        validator = ContinuityValidator(db_conn_getter=lambda: self.conn)
        event = {'type': 'faction_event', 'source_faction_id': self.fid_a, 'target_faction_id': self.fid_b, 'action': 'attack'}
        valid, reason = validator.validate_event(event)
        self.assertFalse(valid)
        self.assertIn('ally', reason.lower())

    def test_cooldown_expired_allows_attack(self):
        c = self.conn.cursor()
        import time
        now = int(time.time())
        # cooldown in the past
        c.execute('INSERT INTO faction_relationships (source_faction_id, target_faction_id, relationship_type, strength, cooldown_until) VALUES (?, ?, ?, ?, ?)', (self.fid_a, self.fid_b, 'rival', -0.6, now - 10))
        self.conn.commit()
        from src.services.continuity import ContinuityValidator
        validator = ContinuityValidator(db_conn_getter=lambda: self.conn)
        event = {'type': 'faction_event', 'source_faction_id': self.fid_a, 'target_faction_id': self.fid_b, 'action': 'attack'}
        valid, reason = validator.validate_event(event)
        self.assertTrue(valid)


if __name__ == '__main__':
    unittest.main()
