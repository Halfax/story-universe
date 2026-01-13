import os
import tempfile
import unittest

from services.arc_persistence import (
    init_db,
    create_arc,
    get_arc,
    list_arcs,
    update_arc,
    delete_arc,
)


class ArcPersistenceTests(unittest.TestCase):
    def setUp(self):
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.close()
        self.db_path = tf.name
        init_db(self.db_path)

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_create_get_list_update_delete(self):
        arc = {
            'id': 'arc-1',
            'name': 'Test Arc',
            'state': 'active',
            'participants': ['c1', 'c2'],
            'events': [],
            'goals': [{'goal': 'explore'}],
            'data': {'progress': 0},
        }
        create_arc(self.db_path, arc)
        fetched = get_arc(self.db_path, 'arc-1')
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched['id'], 'arc-1')
        self.assertEqual(fetched['name'], 'Test Arc')
        self.assertEqual(fetched['state'], 'active')
        self.assertIn('progress', fetched['data'])
        self.assertEqual(fetched['participants'], ['c1', 'c2'])
        self.assertEqual(fetched['goals'][0]['goal'], 'explore')

        all_arcs = list_arcs(self.db_path)
        self.assertTrue(len(all_arcs) >= 1)

        updated = update_arc(self.db_path, 'arc-1', {'state': 'completed', 'data': {'progress': 100}})
        self.assertTrue(updated)
        fetched2 = get_arc(self.db_path, 'arc-1')
        self.assertEqual(fetched2['state'], 'completed')
        self.assertEqual(fetched2['data']['progress'], 100)

        deleted = delete_arc(self.db_path, 'arc-1')
        self.assertTrue(deleted)
        self.assertIsNone(get_arc(self.db_path, 'arc-1'))


if __name__ == '__main__':
    unittest.main()
