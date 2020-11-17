# coding: utf-8
import os
import datetime
import pathlib
from schema import Schema, And, Use, SchemaError
from jinjaql.factory import JinJAQL
from jinjaql.convertors import guard_date, escape_string
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestSchemaCases(unittest.TestCase):

    def setUp(self):
        self.sql_root = os.path.abspath(os.path.dirname(__file__))
        self.snaql = JinJAQL(pathlib.Path(self.sql_root, 'queries'))

    def test_usual_case(self):
        news_queries = self.snaql.load_queries('unsafe_news.sql')
        now = datetime.datetime.utcnow()
        schema = Schema({
            'news_id': And(Use(int), lambda i: i > 0),
            'rating': And(Use(float), lambda r: r > 0),
            'date_from': And(Use(guard_date)),
        })
        context = {
            'news_id': '123',
            'date_from': now,
            'rating': 4.22,
        }
        news_queries.select_by_id(schema=schema, **context)

    def test_usual_string_case(self):
        news_queries = self.snaql.load_queries('unsafe_news.sql')
        schema = Schema({
            'slug': And(Use(escape_string), Use(lambda s: "`%s_slug`" % s)),
        })
        context = {
            'slug': 'cool',
        }
        result = news_queries.select_by_slug(schema=schema, **context)
        self.assertEqual(
            result, 'SELECT *\n FROM news\n WHERE slug = `cool_slug`'
        )

    def test_wrong_case(self):
        news_queries = self.snaql.load_queries('unsafe_news.sql')
        now = datetime.datetime.utcnow()
        schema = Schema({
            'news_id': And(Use(int), lambda i: i > 0),
            'rating': And(Use(float), lambda r: r > 0),
            'date_from': And(Use(guard_date)),
        })
        context = {
            'news_id': '0',
            'date_from': now,
            'rating': 4.22,
        }
        with self.assertRaises(SchemaError):
            news_queries.select_by_id(schema=schema, **context)
