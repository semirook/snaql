# coding: utf-8
import os
import datetime
import pathlib
from jinjaql.factory import JinJAQL, SnaqlException
from jinjaql.convertors import SnaqlGuardException
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestGuards(unittest.TestCase):

    def setUp(self):
        self.sql_root = os.path.abspath(os.path.dirname(__file__))
        self.snaql = JinJAQL(pathlib.Path(self.sql_root, 'queries'))

    def test_guards_normal(self):
        news_queries = self.snaql.load_queries('news.sql')
        date = datetime.datetime.now()
        self.assertEqual(
            news_queries.select_by_id(
                news_id=10,
                date_from=date,
                rating='5.6',
            ), (
                "SELECT *\n FROM news\n "
                "WHERE id = 10\n "
                "AND creation_date >= "
                "'{0.year:04}-{0.month:02}-{0.day:02} "
                "{0.hour:02}:{0.minute:02}:{0.second:02}.{0.microsecond:06}'\n "
                "AND rating >= 5.6"
            ).format(date)
        )

    def test_guard_integer_exc(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertRaises(
            SnaqlGuardException,
            news_queries.select_by_id,
            news_id='mouse'
        )

    def test_guard_datetime_exc(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertRaises(
            SnaqlGuardException,
            news_queries.select_by_id,
            date_from='tomorrow'
        )

    def test_guard_case_exc(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertRaises(
            SnaqlGuardException,
            news_queries.get_news,
            sort_order='REV'
        )

    def test_guard_case(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertEqual(
            news_queries.get_news(sort_order='ASC'),
            'SELECT *\n FROM news\n  ORDER BY creation_date ASC'
        )

    def test_guard_regexp(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertEqual(
            news_queries.select_by_slug(slug='latest_news'),
            "SELECT *\n FROM news\n WHERE slug = 'latest_news'"
        )

    def test_guard_exc(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertRaises(
            SnaqlGuardException,
            news_queries.select_by_slug,
            slug='latest news',
        )

    def test_conditions_sugar_without_context(self):
        news_queries = self.snaql.load_queries('news.sql')
        response = news_queries.get_news(conditions=[
            news_queries.cond_ids_in_news,
            news_queries.cond_date_from_news,
            news_queries.cond_date_to_news,
        ])
        self.assertEqual(response, 'SELECT *\n FROM news')

    def test_conditions_sugar_with_context(self):
        news_queries = self.snaql.load_queries('news.sql')
        today = datetime.date.today()
        context = {
            'ids': (1, 2, 3),
            'date_from': today,
            'sort_order': 'ASC',
        }
        response = news_queries.get_news(conditions=[
            news_queries.cond_ids_in_news,
            news_queries.cond_date_from_news,
            news_queries.cond_date_to_news,
        ], **context)
        self.assertEqual(
            response, (
                "SELECT *\n FROM news\n WHERE id IN (1, 2, 3) "
                "AND creation_date >= "
                "'{0.year:04}-{0.month:02}-{0.day:02}' "
                "ORDER BY creation_date ASC"
            ).format(today)
        )

    def test_conditions_sugar_wrong_context(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertRaises(
            SnaqlException,
            news_queries.get_news,
            conditions=[news_queries.cond_date_to_another_news]
        )

    def test_conditions_sugar_outside_context(self):
        news_queries = self.snaql.load_queries('news.sql')
        self.assertRaises(
            SnaqlException,
            news_queries.cond_date_to_another_news,
        )
