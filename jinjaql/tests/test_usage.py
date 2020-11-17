# coding: utf-8
import os
import datetime
import pathlib
from jinjaql.factory import JinJAQL
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestUseCases(unittest.TestCase):

    def setUp(self):
        self.sql_root = os.path.abspath(os.path.dirname(__file__))
        self.snaql = JinJAQL(pathlib.Path(self.sql_root, 'queries'))

    def test_usual_case(self):
        users_queries = self.snaql.load_queries('users.sql')
        self.assertEqual(
            users_queries.users_by_country(), (
                "SELECT count(*) AS count\n "
                "FROM user\n "
                "WHERE country_code = 'UA'"
            )
        )
        self.assertEqual(
            users_queries.select_all(), (
                "SELECT * "
                "FROM user"
            )
        )

    def test_subrendering(self):
        users_queries = self.snaql.load_queries('users.sql')

        self.assertEqual(
            users_queries.users_count_cond(), (
                "SELECT count(*) AS count\n "
                "FROM user\n "
            )
        )
        context = {'by_country': True, 'country_code': 42}
        self.assertEqual(
            users_queries.users_count_cond(**context), (
                "SELECT count(*) AS count\n "
                "FROM user\n "
                "WHERE country_code = 42"
            )
        )

    def test_complex_subrendering(self):
        users_queries = self.snaql.load_queries('users.sql')

        context = {'users_ids': [1, 2, 3]}
        self.assertEqual(
            users_queries.users_select_cond(**context), (
                "SELECT *\n "
                "FROM user\n "
                "WHERE user_id IN (1, 2, 3)"
            )
        )

    def test_escaping(self):
        users_queries = self.snaql.load_queries('users.sql')

        context = {'user_name': "semirook"}
        self.assertEqual(
            users_queries.users_escaping(**context), (
                "SELECT *\n FROM user\n "
                "WHERE user_name = 'semirook'"
            )
        )

    def test_clean_env(self):
        users_queries = self.snaql.load_queries('users.sql')
        self.assertEqual(
            users_queries.select_all(), (
                "SELECT * "
                "FROM user"
            )
        )
        self.assertFalse(self.snaql.jinja_env.sql_params)

    def test_multiple_ns(self):
        users_queries = self.snaql.load_queries('users.sql')
        news_queries = self.snaql.load_queries('news.sql')
        self.assertEqual(
            users_queries.select_all(), (
                "SELECT * "
                "FROM user"
            )
        )
        self.assertEqual(
            news_queries.select_all(), (
                "SELECT *\n "
                "FROM news"
            )
        )

    def test_guards(self):
        news_queries = self.snaql.load_queries('news.sql')
        news_queries.select_by_id(
            news_id=10,
            date_from=datetime.datetime.now(),
            rating='5.6',
        )

    def test_simple_tmpl(self):
        queries = self.snaql.load_queries('integration.sql')
        result_list = queries.simple_tmpl(var=[1, 2, 3])
        self.assertEqual(result_list, '[1, 2, 3]')

        result_dict = queries.simple_tmpl(var={'a': 1, 'b': 2})
        self.assertTrue(
            result_dict in ("{'a': 1, 'b': 2}", "{'b': 2, 'a': 1}")
        )

    def test_tmpl_with_comment(self):
        users_queries = self.snaql.load_queries('users.sql')
        abc = users_queries.select_all_with_comment()
