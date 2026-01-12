import sqlite3
import json
import time
import unittest

from src.services.continuity import ContinuityValidator, PERSONA_COOLDOWN_SECONDS, PERSONA_DRIFT_DELTAS, PERSONA_INERTIA_DEFAULT
import src.services.continuity as continuity_mod

class TestPersonalityDrift(unittest.TestCase):
    def setUp(self):
        # in-memory DB
        self.conn = sqlite3.connect(':memory:')
        cur = self.conn.cursor()
        # create minimal factions and cooldowns tables used by continuity.apply_event_consequences
        cur.execute('CREATE TABLE factions (id INTEGER PRIMARY KEY, name TEXT, personality_traits TEXT)')
        cur.execute('CREATE TABLE faction_cooldowns (faction_id INTEGER, cooldown_key TEXT, until_ts INTEGER)')
        cur.execute('CREATE TABLE faction_relationships (source_faction_id INTEGER, target_faction_id INTEGER, relationship_type TEXT, strength REAL, cooldown_until INTEGER)')
        self.conn.commit()
        # insert a faction with neutral traits
        traits = {'aggressive': 0.0}
        cur.execute('INSERT INTO factions (id,name,personality_traits) VALUES (?,?,?)', (1, 'Red Faction', json.dumps(traits)))
        self.conn.commit()
        # speed up cooldowns for tests
        self._orig_cool = continuity_mod.PERSONA_COOLDOWN_SECONDS
        self._orig_inertia = continuity_mod.PERSONA_INERTIA_DEFAULT
        continuity_mod.PERSONA_COOLDOWN_SECONDS = 1
        continuity_mod.PERSONA_INERTIA_DEFAULT = 0.0

    def tearDown(self):
        continuity_mod.PERSONA_COOLDOWN_SECONDS = self._orig_cool
        continuity_mod.PERSONA_INERTIA_DEFAULT = self._orig_inertia
        try:
            self.conn.close()
        except Exception:
            pass

    def test_drift_applies_and_respects_cooldown(self):
        v = ContinuityValidator(db_conn_getter=lambda: self.conn)
        ev = {'type': 'faction_event', 'action': 'attack', 'source_faction_id': 1, 'target_faction_id': 2}
        # first application should increase 'aggressive'
        v.apply_event_consequences(ev, db_conn=self.conn)
        cur = self.conn.cursor()
        cur.execute('SELECT personality_traits FROM factions WHERE id = ?', (1,))
        row = cur.fetchone()
        p = json.loads(row[0])
        self.assertGreater(p.get('aggressive', 0.0), 0.0)
        first_val = p.get('aggressive', 0.0)
        # immediate second application should be blocked by cooldown -> no change
        v.apply_event_consequences(ev, db_conn=self.conn)
        cur.execute('SELECT personality_traits FROM factions WHERE id = ?', (1,))
        row = cur.fetchone()
        p2 = json.loads(row[0])
        self.assertAlmostEqual(p2.get('aggressive', 0.0), first_val, places=6)
        # wait for cooldown to expire, then apply again -> accumulation
        time.sleep(1.1)
        v.apply_event_consequences(ev, db_conn=self.conn)
        cur.execute('SELECT personality_traits FROM factions WHERE id = ?', (1,))
        row = cur.fetchone()
        p3 = json.loads(row[0])
        self.assertGreater(p3.get('aggressive', 0.0), first_val)

    def test_clamping(self):
        # ensure traits do not exceed 1.0
        cur = self.conn.cursor()
        # set aggressive very high
        cur.execute('UPDATE factions SET personality_traits = ? WHERE id = ?', (json.dumps({'aggressive': 0.99}), 1))
        self.conn.commit()
        v = ContinuityValidator(db_conn_getter=lambda: self.conn)
        ev = {'type': 'faction_event', 'action': 'attack', 'source_faction_id': 1, 'target_faction_id': 2}
        # set drift large by temporarily adjusting delta
        orig = continuity_mod.PERSONA_DRIFT_DELTAS.copy()
        continuity_mod.PERSONA_DRIFT_DELTAS['attack'] = {'aggressive': 0.5}
        # set inertia zero so full delta applies
        orig_inertia = continuity_mod.PERSONA_INERTIA_DEFAULT
        continuity_mod.PERSONA_INERTIA_DEFAULT = 0.0
        # speed cooldown
        orig_cool = continuity_mod.PERSONA_COOLDOWN_SECONDS
        continuity_mod.PERSONA_COOLDOWN_SECONDS = 1
        v.apply_event_consequences(ev, db_conn=self.conn)
        cur.execute('SELECT personality_traits FROM factions WHERE id = ?', (1,))
        row = cur.fetchone()
        p = json.loads(row[0])
        self.assertLessEqual(p.get('aggressive', 0.0), 1.0)
        # restore
        continuity_mod.PERSONA_DRIFT_DELTAS = orig
        continuity_mod.PERSONA_INERTIA_DEFAULT = orig_inertia
        continuity_mod.PERSONA_COOLDOWN_SECONDS = orig_cool


if __name__ == '__main__':
    unittest.main()
