import unittest
import sqlite3
from pathlib import Path


class TestContinuityValidatorFactionMetrics(unittest.TestCase):
    def setUp(self):
        # Create an in-memory DB and apply schema (chronicle-keeper/src/db/schema.sql)
        schema_path = Path(__file__).resolve().parents[1] / 'src' / 'db' / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        self.conn = sqlite3.connect(':memory:')
        self.conn.executescript(schema)
        # ensure a character exists to avoid validator fallback
        c = self.conn.cursor()
        c.execute('INSERT INTO characters (name, age, traits, location_id, status) VALUES (?, ?, ?, ?, ?)', ('Tester', 30, '[]', NULL, 'alive') if False else ('Tester', 30, '[]', None, 'alive'))
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_low_trust_blocks_alliance(self):
        # Insert faction and low trust metrics
        c = self.conn.cursor()
        c.execute('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', ('LowTrust', None, '{}'))
        fid = c.lastrowid
        c.execute('INSERT INTO faction_metrics (faction_id, trust, power, resources, influence) VALUES (?, ?, ?, ?, ?)', (fid, 0.05, 1, 10, 0))
        self.conn.commit()

        # Import validator with db_conn_getter that returns our connection
        from services.continuity import ContinuityValidator
        validator = ContinuityValidator(db_conn_getter=lambda: self.conn)

        event = {'type': 'faction_event', 'source_faction_id': fid, 'target_faction_id': fid, 'action': 'form_alliance'}
        valid, reason = validator.validate_event(event)
        self.assertFalse(valid)
        self.assertIn('trust', reason)

    def test_high_trust_allows_alliance(self):
        c = self.conn.cursor()
        c.execute('INSERT INTO factions (name, ideology, relationships) VALUES (?, ?, ?)', ('HighTrust', None, '{}'))
        fid = c.lastrowid
        c.execute('INSERT INTO faction_metrics (faction_id, trust, power, resources, influence) VALUES (?, ?, ?, ?, ?)', (fid, 0.8, 5, 100, 10))
        self.conn.commit()

        from services.continuity import ContinuityValidator
        validator = ContinuityValidator(db_conn_getter=lambda: self.conn)
        event = {'type': 'faction_event', 'source_faction_id': fid, 'target_faction_id': fid, 'action': 'form_alliance'}
        valid, reason = validator.validate_event(event)
        print('\nDEBUG high-trust reason ->', valid, reason)
        self.assertTrue(valid)


if __name__ == '__main__':
    unittest.main()
