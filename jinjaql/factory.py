# coding: utf-8
import os
import copy
import collections
import types
import sys
import functools
from collections import namedtuple
import pathlib

from jinja2 import nodes
from jinja2 import Environment, TemplateNotFound, FileSystemLoader
from jinja2.ext import Extension
from jinja2.loaders import split_template_path
from jinja2.utils import open_if_exists
from schema import Schema

from jinjaql.convertors import (
    guard_bool,
    guard_case,
    guard_date,
    guard_datetime,
    guard_float,
    guard_integer,
    guard_regexp,
    guard_string,
    guard_time,
    guard_timedelta,
)

import jinjaql.engine as engine


PY = sys.version_info
PY3K = PY >= (3, 0, 0)


class RawFileSystemLoader(FileSystemLoader):

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = os.path.join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = os.path.getmtime(filename)
            # Need to save original raw template before compilation
            environment.sql_params.setdefault('raws', {}).update({
                template: [c.strip() for c in contents.splitlines()]
            })

            def uptodate():
                try:
                    return os.path.getmtime(filename) == mtime
                except OSError:
                    return False
            return contents, filename, uptodate

        raise TemplateNotFound(template)


class JinjaSQLExtension(Extension):
    tags = set(['sql', 'query'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        expr = parser.parse_expression()
        args = [expr]
        kwargs = [nodes.Keyword('func', expr)]
        if parser.stream.skip_if('comma'):
            # Optional 'note' for function docstring
            if (
                parser.stream.current.type == 'name' and
                parser.stream.current.value in (
                    'note',
                    'cond_for',
                    'depends_on',
                    'connection_string', #TODO
                )
            ):
                stream_type = parser.stream.current.value
                next(parser.stream)
                parser.stream.expect('assign')
                # Depends meta is always a list
                if stream_type == 'depends_on':
                    c_expr = parser.parse_list()
                else:
                    c_expr = parser.parse_expression()
                args.append(c_expr)
                kwargs.append(nodes.Keyword(stream_type, c_expr))

        body = parser.parse_statements(
            ['name:endsql', 'name:endquery'], drop_needle=True
        )
        raw_template = self.environment.sql_params['raws'][parser.name]

        # Lines range of original raw template
        raw_lines = slice(lineno, parser.stream.current.lineno-1)
        self.environment.sql_params.setdefault('funcs', {}).update({
            expr.value: {'raw_sql': '\n '.join(raw_template[raw_lines])}
        })
        call_node = nodes.Call(
            self.attr('_sql_process', lineno=lineno),
            args, kwargs, None, None
        )
        return nodes.CallBlock(call_node, [], [], body)

    def _sql_process(self, *args, **kwargs):
        caller = kwargs['caller']
        raw_sql = '\n '.join(x.strip() for x in caller().split('\n') if x)
        if 'cond_for' in kwargs:
            origin = (
                self.environment.sql_params['funcs'].get(kwargs['cond_for'])
            )
            if origin:
                origin.setdefault('conds', []).append(kwargs['cond_for'])

        origin = self.environment.sql_params['funcs'].get(kwargs['func'])
        origin.update({
            'sql': raw_sql,
            'note': kwargs.get('note'),
            'is_cond': 'cond_for' in kwargs,
            'depends_on': kwargs.get('depends_on', []),
            'connection_string': kwargs.get('connection_string'),#TODO
            'node': None,
        })
        if origin['is_cond']:
            origin['cond_for'] = kwargs['cond_for']

        return raw_sql


class SnaqlDepNode(object):

    def __init__(self, name):
        self.name = name
        self.edges = []

    def add_edge(self, node):
        self.edges.append(node)

    def __str__(self):
        return '<SnaqlDepNode %s>' % self.name

    def __repr__(self):
        return '<SnaqlDepNode %s>' % self.name


class SnaqlException(Exception):
    pass


class JinJAQL(object):

    def __init__(
            self,
            folder_path: pathlib.Path,
            engine=engine.default,
            cache=False,
    ):
        folder_path = pathlib.Path(folder_path)
        self.jinja_env = Environment(
            trim_blocks=True,
            extensions=[JinjaSQLExtension],
            loader=RawFileSystemLoader(folder_path)
        )
        self.jinja_env.filters.update({
            'guards.string': guard_string,
            'guards.integer': guard_integer,
            'guards.datetime': guard_datetime,
            'guards.date': guard_date,
            'guards.float': guard_float,
            'guards.timedelta': guard_timedelta,
            'guards.time': guard_time,
            'guards.case': guard_case,
            'guards.regexp': guard_regexp,
            'guards.bool': guard_bool,
        })
        self.jinja_env.extend(sql_params={})
        self._engine = engine
        self._cache = cache

    def gen_func(self, name, meta_struct, env):

        def subrender_cond(owner_name, cond_func, context):
            if (
                isinstance(cond_func, collections.abc.Callable) and
                cond_func.is_cond
            ):
                cond_struct = meta_struct['funcs'][cond_func.func_name]
                if cond_struct['cond_for'] != owner_name:
                    raise SnaqlException(
                        '"%s" is not proper condition for "%s"' % (
                            cond_func.func_name,
                            owner_name
                        )
                    )
                cond_tmpl = env.from_string(
                    meta_struct['funcs'][cond_func.func_name]['raw_sql']
                )
                return cond_tmpl.render(**context).strip()
            return cond_func

        def fn(**kwargs):
            if meta_struct['funcs'][name]['is_cond']:
                raise SnaqlException((
                    '"%s" is condition for "%s" and can not '
                    'be rendered outside of it\'s scope'
                ) % (name, meta_struct['funcs'][name]['cond_for']))

            if kwargs:
                for point, val in kwargs.items():
                    maybe_cond_sql = subrender_cond(name, val, kwargs)
                    if maybe_cond_sql:
                        kwargs[point] = maybe_cond_sql
                    if (
                        isinstance(val, collections.abc.Iterable) and
                        not isinstance(
                            val, (str if PY3K else types.StringTypes, dict)
                        )
                    ):
                        val = [subrender_cond(name, v, kwargs) for v in val]
                        kwargs[point] = [v for v in val if v]

                if 'schema' in kwargs and isinstance(kwargs['schema'], Schema):
                    validation_schema = kwargs.pop('schema')
                    kwargs = validation_schema.validate(kwargs)

                sql_tmpl = (
                    env.from_string(meta_struct['funcs'][name]['raw_sql'])
                )
                return self._engine(
                    query_string=sql_tmpl.render(**kwargs).strip(),
                    connection_string=meta_struct['funcs'][name]['connection_string'],
                ) #TODO

            return meta_struct['funcs'][name]['sql']

        fn.__doc__ = meta_struct['funcs'][name]['note']
        fn.is_cond = meta_struct['funcs'][name]['is_cond']
        fn.func_name = str(name)
        if self._cache:
            cache_fn = functools.lru_cache()(fn)
            return cache_fn
        else:
            return fn

    def gen_dep_graph(self, node, accum):
        for edge in node.edges:
            if edge not in accum:
                self.gen_dep_graph(edge, accum)

        accum.append(node)

        return accum

    def load_queries(self, sql_path):
        template = self.jinja_env.get_template(sql_path)
        template.render()

        factory_methods = {}
        meta_struct = copy.deepcopy(self.jinja_env.sql_params)
        blocks = set(meta_struct['funcs'])

        node = SnaqlDepNode('root')

        for name, block in meta_struct['funcs'].items():
            # Dependency graph building
            block['node'] = block['node'] or SnaqlDepNode(name)
            for dep in block['depends_on']:
                if dep not in blocks:
                    raise SnaqlException(
                        '"%s" block not found in "%s"' % (dep, sql_path)
                    )
                if meta_struct['funcs'][dep]['node'] is None:
                    meta_struct['funcs'][dep]['node'] = SnaqlDepNode(dep)

                block['node'].add_edge(meta_struct['funcs'][dep]['node'])

            node.add_edge(block['node'])

            fn = self.gen_func(name, meta_struct, self.jinja_env)
            factory_methods[name] = fn

        edges_accum = []
        graph = self.gen_dep_graph(node, edges_accum)
        graph.pop()  # root node

        factory_methods['ordered_blocks'] = [
            factory_methods[n.name]
            for n in graph
        ]

        factory = namedtuple('SQLFactory', factory_methods.keys())
        struct = factory(*factory_methods.values())
        self.jinja_env.sql_params.clear()

        return struct
