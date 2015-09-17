# coding: utf-8
import os
from snaql.factory import Snaql, SnaqlException
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestMigrations(unittest.TestCase):

    def setUp(self):
        self.sql_root = os.path.abspath(os.path.dirname(__file__))
        self.snaql = Snaql(self.sql_root, 'queries')

    def test_guard_integer_exc(self):
        migrate_queries = self.snaql.load_queries('migrations.sql')
        call_order = [fn.func_name for fn in migrate_queries.ordered_blocks]
        # Both are possible, flavors and templates have no dependencies
        # and their order does not matter
        self.assertTrue(
            call_order in (
                [
                    'create_flavors',
                    'create_templates',
                    'create_nodes',
                    'create_clusters'
                ],
                [
                    'create_templates',
                    'create_flavors',
                    'create_nodes',
                    'create_clusters'
                ],
            )
        )
