# coding: utf-8
import os
from snaql.factory import Snaql, SnaqlException
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestMigrations(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'queries'
        )
        self.snaql = Snaql(self.path)

    def test_guard_integer_exc(self):
        migrate_queries = self.snaql.load_queries('migrations.sql')
        call_order = [fn.func_name for fn in migrate_queries.ordered_blocks]
        # All of these solutions are valid
        possible_solutions = (
            [
                'create_templates',
                'create_clusters',
                'create_dummy',
                'create_flavors',
                'create_nodes',
            ],
            [
                'create_templates',
                'create_dummy',
                'create_flavors',
                'create_nodes',
                'create_clusters',
            ],
            [
                'create_templates',
                'create_dummy',
                'create_clusters',
                'create_nodes',
                'create_clusters',
            ],
            [
                'create_templates',
                'create_dummy',
                'create_clusters',
                'create_flavors',
                'create_nodes',
            ],
            [
                'create_templates',
                'create_dummy',
                'create_flavors',
                'create_clusters',
                'create_nodes',
            ],
        )
        self.assertTrue(call_order in possible_solutions)
