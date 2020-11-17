# coding: utf-8
import os
import shutil
import sqlite3
import pathlib
from jinjaql.factory import JinJAQL

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.sql_root = os.path.abspath(os.path.dirname(__file__))
        self.snaql = JinJAQL(pathlib.Path(self.sql_root, 'queries'))
        self.sqlite_folder = os.path.join(self.sql_root, 'data')
        self.sqlite_path = os.path.join(self.sqlite_folder, 'test_db.sqlite')
        if not os.path.exists(self.sqlite_folder):
            os.makedirs(self.sqlite_folder)
        if not os.path.exists(self.sqlite_path):
            open(self.sqlite_path, 'a').close()

    def tearDown(self):
        shutil.rmtree(self.sqlite_folder)

    def test_req(self):
        queries = self.snaql.load_queries('integration.sql')
        conn = sqlite3.connect(self.sqlite_path)
        conn.execute(queries.create_artists())
        query = queries.insert_artist(**{
            'id': 1,
            'name': 'Lana Del Rey',
            'age': 30,
            'instrument': 'voice',
            'creation_date': '2015-10-13',
        })
        conn.execute(query)
        conn.commit()
        conn.close()

        conn = sqlite3.connect(self.sqlite_path)
        query = queries.get_artists(id=1)
        response = conn.execute(query)

        self.assertEqual(response.fetchone(), ('Lana Del Rey', 30, 'voice'))
        conn.close()